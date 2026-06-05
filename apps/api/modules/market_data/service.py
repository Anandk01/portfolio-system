import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from core.config import settings

class MarketDataService:
    def __init__(self):
        self.data_dir = os.path.join(os.getcwd(), "data", "market_data")
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_historical_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> str:
        """
        Fetches historical data for a symbol.
        Returns the path to the saved Parquet file.
        """
        # specialized cleaning for NSE symbols if not present
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            # logic to append .NS if it looks like an Indian stock (simple heuristic)
            # In production, use the asset mapper's accurate symbol
            ticker_symbol = f"{symbol}.NS"
        else:
            ticker_symbol = symbol

        file_path = os.path.join(self.data_dir, f"{ticker_symbol}.parquet")
        
        # Simple Cache Check: if file exists and is modified today, return it
        if os.path.exists(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime.date() == datetime.now().date():
                print(f"Using cached data for {ticker_symbol}")
                return file_path

        print(f"Fetching data for {ticker_symbol} from yfinance...")
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for symbol {ticker_symbol}")
            
        # Clean and Save
        df.reset_index(inplace=True)
        # Ensure 'Date' is datetime and tz-naive for Parquet compatibility
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            if hasattr(df['Date'].dt, 'tz') and df['Date'].dt.tz is not None:
                df['Date'] = df['Date'].dt.tz_localize(None)
        
        # Strip TZ from any other datetime columns for stability
        for col in df.select_dtypes(include=['datetime64[ns, Asia/Kolkata]', 'datetimetz']).columns:
            df[col] = df[col].dt.tz_localize(None)

        # Save using default engine (pyarrow is more stable for timestamps)
        df.to_parquet(file_path, index=False)
            
        return file_path

    def get_latest_price(self, symbol: str) -> float:
        """
        Get real-time (delayed) price.
        """
        # Similar logic
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        ticker = yf.Ticker(symbol)
        # fast fetch
        todays_data = ticker.history(period="1d")
        if not todays_data.empty:
            return float(todays_data['Close'].iloc[-1])
        return 0.0

    def get_company_profile(self, symbol: str) -> dict:
        """
        Fetch company profile (sector, industry) from Yahoo Finance.
        """
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol = f"{symbol}.NS"
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "sector": info.get("sector", "Others"),
                "industry": info.get("industry", "Others"),
                "longBusinessSummary": info.get("longBusinessSummary", "")
            }
        except Exception as e:
            print(f"Error fetching profile for {symbol}: {e}")
            return {"sector": "Others", "industry": "Others"}

market_data_service = MarketDataService()
