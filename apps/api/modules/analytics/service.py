import numpy as np
import pandas as pd
from typing import List, Dict
from core.models import NormalizedHolding, AssetType


class AnalyticsEngine:

    def calculate_portfolio_metrics(
        self,
        holdings: List[NormalizedHolding],
        market_data_map: Dict[str, pd.DataFrame],
    ) -> Dict:
        """
        Calculate portfolio-level metrics using available data.
        Resilient to Mutual Funds and sparse historical data.
        """
        if not holdings:
            return {}

        # ------------------------------------------------------------------
        # 1️⃣ TOTAL VALUE (ALL ASSETS)
        # ------------------------------------------------------------------
        # Include STOCK, ETF, and MF in the total value calculation
        total_value = sum(h.current_value for h in holdings)
        
        if total_value <= 0:
            return {}

        # Calculate weights for ALL assets for diversification scoring
        all_weights = {h.asset_name: h.current_value / total_value for h in holdings}

        # ------------------------------------------------------------------
        # 2️⃣ FILTER PRICEABLE ASSETS FOR PERFORMANCE METRICS
        # ------------------------------------------------------------------
        priceable_holdings = [
            h for h in holdings
            if h.asset_type in (AssetType.STOCK, AssetType.ETF)
            and h.symbol
            and h.current_value > 0
        ]

        # ------------------------------------------------------------------
        # 3️⃣ BUILD RETURNS MATRIX
        # ------------------------------------------------------------------
        returns_df = pd.DataFrame()
        active_weights: Dict[str, float] = {}
        
        # Calculate localized weights just for the priceable subset (for Sharpe/Vol)
        priceable_total = sum(h.current_value for h in priceable_holdings)

        for h in priceable_holdings:
            df = market_data_map.get(h.symbol)

            if df is None or df.empty or "Close" not in df.columns:
                print(f"DEBUG: No market data found for {h.symbol}")
                continue

            # Ensure we have a Date index for alignment
            if "Date" in df.columns:
                temp_df = df.set_index("Date")["Close"]
            else:
                temp_df = df["Close"]

            # Calculate returns
            returns = temp_df.pct_change()

            if returns.dropna().empty:
                continue

            returns_df[h.symbol] = returns
            active_weights[h.symbol] = h.current_value / priceable_total if priceable_total > 0 else 0

        # ------------------------------------------------------------------
        # 4️⃣ DEFAULT METRICS
        # ------------------------------------------------------------------
        default_metrics = {
            "total_value": round(total_value, 2),
            "annual_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "VaR_95_daily": 0.0,
            "diversification_score": self._calculate_diversification(all_weights),
        }

        if returns_df.empty:
            print(f"DEBUG: returns_df is empty. Priceable count: {len(priceable_holdings)}")
            return default_metrics

        # ------------------------------------------------------------------
        # 5️⃣ ALIGN RETURNS + WEIGHTS (HYPER-RESILIENT)
        # ------------------------------------------------------------------
        # Use forward fill to handle different trading days
        print(f"DEBUG: returns_df pre-alignment: {returns_df.shape}")
        
        # Sort index to ensure ffill works correctly
        returns_df.sort_index(inplace=True)
        
        # Fill gaps. fillna(0) ensures that we don't drop rows where only SOME assets have data.
        # This is CRITICAL for portfolios with assets that have different listing dates.
        returns_df = returns_df.ffill().fillna(0)
        
        print(f"DEBUG: returns_df post-alignment: {returns_df.shape}")

        if returns_df.empty:
            print("DEBUG: returns_df is still empty after filling. Returning default.")
            return default_metrics

        # Normalize weights for the symbols that actually made it into the matrix
        weight_vector = np.array([active_weights[s] for s in returns_df.columns])
        print(f"DEBUG: Weight vector: {weight_vector}")
        if weight_vector.sum() > 0:
            weight_vector = weight_vector / weight_vector.sum()
        else:
            print("DEBUG: Weight vector sum is 0. Returning default.")
            return default_metrics

        # ------------------------------------------------------------------
        # 6️⃣ PORTFOLIO PERFORMANCE
        # ------------------------------------------------------------------
        portfolio_returns = returns_df.dot(weight_vector)
        print(f"DEBUG: Portfolio returns count: {len(portfolio_returns)}")

        mean_daily_return = portfolio_returns.mean()
        std_daily_return = portfolio_returns.std()
        print(f"DEBUG: Mean: {mean_daily_return}, Std: {std_daily_return}")

        # Metrics
        annual_volatility = std_daily_return * np.sqrt(252)
        annual_return = mean_daily_return * 252
        risk_free_rate = 0.05

        sharpe_ratio = (
            (annual_return - risk_free_rate) / annual_volatility
            if annual_volatility > 0.0001
            else 0.0
        )

        # Value at Risk (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5) if not portfolio_returns.empty else 0.0

        return {
            "total_value": round(total_value, 2),
            "annual_volatility": round(float(annual_volatility), 4),
            "sharpe_ratio": round(float(sharpe_ratio), 2),
            "VaR_95_daily": round(float(var_95), 4),
            "diversification_score": self._calculate_diversification(all_weights),
        }

    # ----------------------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------------------

    def calculate_historical_returns(
        self,
        holdings: List[NormalizedHolding],
        market_data_map: Dict[str, pd.DataFrame]
    ) -> pd.Series:
        """
        Calculates the historical daily returns series for the portfolio.
        Used for benchmarking and volatility analysis.
        """
        priceable_holdings = [
            h for h in holdings
            if h.asset_type in (AssetType.STOCK, AssetType.ETF)
            and h.symbol
            and h.current_value > 0
        ]
        
        if not priceable_holdings:
            return pd.Series(dtype=float)

        returns_df = pd.DataFrame()
        active_weights = {}
        priceable_total = sum(h.current_value for h in priceable_holdings)

        for h in priceable_holdings:
            df = market_data_map.get(h.symbol)
            if df is None or df.empty or "Close" not in df.columns: continue
            
            if "Date" in df.columns:
                temp_df = df.set_index("Date")["Close"]
            else:
                temp_df = df["Close"]

            rets = temp_df.pct_change()
            if not rets.empty:
                returns_df[h.symbol] = rets
                active_weights[h.symbol] = h.current_value / priceable_total

        if returns_df.empty: return pd.Series(dtype=float)

        # Align
        returns_df.sort_index(inplace=True)
        returns_df = returns_df.ffill().fillna(0)
        
        # Weighted Aggregation
        weight_vector = np.array([active_weights[col] for col in returns_df.columns])
        # Re-normalize if some assets dropped
        if weight_vector.sum() > 0:
            weight_vector = weight_vector / weight_vector.sum()
            
        portfolio_returns = returns_df.dot(weight_vector)
    
        # 5. ANOMALY DETECTION & SMOOTHING (User Requirement)
        # If a daily or cumulative drop is extreme (>-50% suddenly) without sell data,
        # we treat it as a data gap and "carry forward" or smooth it.
        # Note: In Phase 1, we don't have full transaction history, so we assume 
        # extreme drops in projected historical prices are likely data anomalies.
        
        # We'll use a 7-day rolling window to detect outliers or just check monthly jumps
        # But simpler: if portfolio_returns has any values < -0.5 (50% drop in one day)
        # clip it and log as anomaly.
        
        if not portfolio_returns.empty:
            # Detect single day crashes (>50%)
            anomalies = portfolio_returns[portfolio_returns < -0.5]
            if not anomalies.empty:
                print(f"DEBUG: Detected {len(anomalies)} return anomalies. Smoothing...")
                portfolio_returns = portfolio_returns.clip(lower=-0.1) # Max 10% drop per day for projection safety
                
        return portfolio_returns

    def _calculate_diversification(self, weights: Dict[str, float]) -> float:
        """
        Herfindahl-Hirschman Index (HHI) based diversification score.
        """
        if not weights:
            return 0.0

        hhi = sum(w ** 2 for w in weights.values())
        return round(max(0.0, 1 - hhi), 2)

    def calculate_hybrid_score(
        self,
        price_trend_score: float,
        sentiment_score: float,
        volatility: float,
    ) -> float:
        """
        Hybrid Score = 0.6 * Trend + 0.3 * Sentiment + 0.1 * VolPenalty
        """

        # Volatility penalty: higher volatility -> lower score
        vol_component = max(0.0, 1 - (volatility * 2))

        score = (
            0.6 * price_trend_score
            + 0.3 * sentiment_score
            + 0.1 * vol_component
        )

        return round(float(score), 4)


analytics_engine = AnalyticsEngine()
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from core.config import settings

# Ensure model directory exists
os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True)

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class PricePredictor:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{symbol}_lstm.pth")
        self.scaler_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{symbol}_scaler.pkl")
        self.model = None
        self.scaler = None
        self.lookback = 60 # Days to look back

    def _prepare_data(self, df: pd.DataFrame):
        data = df['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i, 0])
            y.append(scaled_data[i, 0])
            
        return np.array(X), np.array(y), scaler

    def train(self, parquet_path: str, epochs=5):
        try:
            df = pd.read_parquet(parquet_path)
            # Basic validation
            if len(df) < self.lookback + 10:
                return {"status": "failed", "reason": "Not enough data points"}

            X, y, scaler = self._prepare_data(df)
            
            # Save scaler
            joblib.dump(scaler, self.scaler_path)
            self.scaler = scaler

            # Convert to tensors
            X_tensor = torch.from_numpy(X).float().unsqueeze(-1) # (N, 60, 1)
            y_tensor = torch.from_numpy(y).float().view(-1, 1)

            # Init Model
            model = LSTMModel()
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

            model.train()
            for epoch in range(epochs):
                outputs = model(X_tensor)
                loss = criterion(outputs, y_tensor)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")

            # Save Model
            torch.save(model.state_dict(), self.model_path)
            self.model = model
            
            return {
                "status": "success", 
                "final_loss": loss.item(), 
                "model_path": self.model_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict_next(self, parquet_path: str):
        if not self.model:
            # Load if exists
            if os.path.exists(self.model_path):
                self.model = LSTMModel()
                self.model.load_state_dict(torch.load(self.model_path))
                self.model.eval()
            else:
                raise ValueError("Model not trained yet.")
        
        if not self.scaler:
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            else:
                raise ValueError("Scaler not found.")

        df = pd.read_parquet(parquet_path)
        last_chunk = df['Close'].values[-self.lookback:].reshape(-1, 1)
        scaled = self.scaler.transform(last_chunk)
        
        input_tensor = torch.from_numpy(scaled).float().unsqueeze(0).unsqueeze(-1) # (1, 60, 1)
        
        with torch.no_grad():
            pred_scaled = self.model(input_tensor)
            
        pred_price = self.scaler.inverse_transform(pred_scaled.numpy())[0][0]
        
        # Calculate trend (simple: next vs current)
        current_price = df['Close'].values[-1]
        trend = "UPWARD" if pred_price > current_price else "DOWNWARD"
        
        return {
            "symbol": self.symbol,
            "current_price": float(current_price),
            "predicted_price": float(pred_price),
            "predicted_trend": trend,
            "confidence": 0.70 # Stub confidence score
        }
from transformers import pipeline
from typing import List, Dict
import torch

class SentimentAnalyzer:
    def __init__(self):
        self.pipeline = None
        self.model_name = "prosusAI/finbert"

    def load_model(self):
        if not self.pipeline:
            print("Loading FinBERT model...")
            # Use GPU if available
            device = 0 if torch.cuda.is_available() else -1
            self.pipeline = pipeline("sentiment-analysis", model=self.model_name, device=device)
            print("FinBERT model loaded.")

    def analyze(self, texts: List[str]) -> Dict[str, float]:
        """
        Analyze a list of texts and return an aggregated sentiment score.
        Score range: -1 (Negative) to +1 (Positive).
        """
        self.load_model()
        results = self.pipeline(texts)
        
        total_score = 0
        count = 0
        
        for res in results:
            label = res['label']
            score = res['score']
            
            # Map labels to numeric values
            # FinBERT labels: positive, negative, neutral
            val = 0
            if label == 'positive':
                val = 1 * score
            elif label == 'negative':
                val = -1 * score
            else: # neutral
                val = 0
                
            total_score += val
            count += 1
            
        avg_score = total_score / count if count > 0 else 0
        
        # Determine overall sentiment label
        overall_sentiment = "NEUTRAL"
        if avg_score > 0.1: overall_sentiment = "POSITIVE"
        elif avg_score < -0.1: overall_sentiment = "NEGATIVE"
        
        return {
            "sentiment": overall_sentiment,
            "sentiment_score": round(avg_score, 4),
            "analyzed_count": count
        }

sentiment_service = SentimentAnalyzer()
