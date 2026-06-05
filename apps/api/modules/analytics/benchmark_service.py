import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class BenchmarkService:
    def __init__(self):
        self.BENCHMARKS = {
            "NIFTY 50": "^NSEI",
            "GOLD": "GOLDBEES.NS"
        }
        self.cache = {} # Simple in-memory cache
        self.data_dir = os.path.join(os.getcwd(), "data", "market_data")
        os.makedirs(self.data_dir, exist_ok=True)

    def get_benchmark_comparison(self, portfolio_returns: pd.Series, period: str = "1y") -> List[Dict[str, Any]]:
        """
        Aligns portfolio returns with Benchmarks.
        Returns visual data for Recharts: [{date: '2024-01-01', portfolio: 105, nifty: 102, gold: 98}, ...]
        """
        if portfolio_returns.empty:
            return []
            
        # 1. Determine Date Range based on Period
        end_date = portfolio_returns.index.max()
        
        days_map = {
            "1mo": 30,
            "6mo": 180,
            "1y": 365,
            "2y": 730
        }
        days = days_map.get(period, 365)
        start_date = end_date - timedelta(days=days)
        
        # Filter Portfolio Returns to requested period
        portfolio_returns = portfolio_returns[portfolio_returns.index >= start_date]
        if portfolio_returns.empty:
            return []
            
        # Re-determine start/end for benchmark fetching
        start_date = portfolio_returns.index.min()
        end_date = portfolio_returns.index.max()
        
        # 2. Fetch Benchmark Data
        benchmark_data = {}
        for name, symbol in self.BENCHMARKS.items():
            df = self._fetch_data(symbol, start_date, end_date)
            if not df.empty:
                # Calculate Cumulative Returns
                # Normalized to start at 0%
                initial_price = df['Close'].iloc[0]
                df['Normalized'] = ((df['Close'] - initial_price) / initial_price) * 100
                benchmark_data[name] = df[['Normalized']]

        # 3. Process Portfolio Returns
        # Portfolio returns are daily % changes. We need cumulative % from start.
        # cumulative = (1 + returns).cumprod() - 1
        portfolio_cum_returns = (1 + portfolio_returns).cumprod() - 1
        portfolio_cum_returns = portfolio_cum_returns * 100 # Convert to %

        # 4. Merge Data (Align Dates)
        # Create master dataframe with Date index
        merged = pd.DataFrame(index=portfolio_returns.index)
        merged['Portfolio'] = portfolio_cum_returns
        
        for name, df in benchmark_data.items():
            # Reindex benchmark to match portfolio dates (ffill for missing days)
            aligned = df.reindex(merged.index, method='ffill')
            merged[name] = aligned['Normalized']

        merged = merged.ffill().fillna(0)
        
        # 5. Format for Charts
        chart_data = []
        for date, row in merged.iterrows():
            item = {
                "date": date.strftime("%Y-%m-%d"),
                "Portfolio": round(row['Portfolio'], 2)
            }
            for name in self.BENCHMARKS.keys():
                if name in row:
                    item[name] = round(row[name], 2)
            chart_data.append(item)
            
        return chart_data

    def _fetch_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetches or loads cached benchmark data.
        """
        # Ensure we cover the range plus a buffer
        start_str = (start_date - timedelta(days=5)).strftime("%Y-%m-%d")
        file_path = os.path.join(self.data_dir, f"{symbol}_bench.parquet")
        
        # Check if cache is fresh (modified today)
        needs_fetch = True
        if os.path.exists(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime.date() == datetime.now().date():
                needs_fetch = False
                
        if needs_fetch:
            print(f"Fetching benchmark {symbol}...")
            try:
                ticker = yf.Ticker(symbol)
                # Fetch generous amount to cover dynamic ranges
                df = ticker.history(period="5y")
                df.reset_index(inplace=True)
                # Timestamp cleanup
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
                
                df.to_parquet(file_path, index=False)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                return pd.DataFrame()

        # Load and Filter
        try:
            df = pd.read_parquet(file_path)
            df.set_index("Date", inplace=True)
            # Slice
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return pd.DataFrame()

benchmark_service = BenchmarkService()
