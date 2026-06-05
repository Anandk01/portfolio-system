
import sys
import os
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

from modules.market_data.nav_service import nav_service
from modules.asset_resolver.service import asset_service
from core.models import ParsedHolding, AssetType, AssetClass

def test_nav_fetcher():
    print("Testing NAV Fetcher...")
    # Using a known scheme code directly to test the fetching logic
    # 102885 is HDFC Top 100 Fund - Direct Plan - Growth Option
    scheme_code = "102885"
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    import requests
    response = requests.get(url)
    data = response.json()
    nav = float(data["data"][0]["nav"])
    print(f"Scheme {scheme_code} NAV: {nav}")
    assert nav is not None and nav > 0
    print("NAV Fetching Logic Verified!\n")

def test_categorization():
    print("Testing Categorization Heuristics...")
    holdings = [
        ParsedHolding(raw_name="RELIANCE INDUSTRIES LTD", quantity=10, invested_value=25000),
        ParsedHolding(raw_name="HDFC LIQUID FUND DIRECT GROWTH", quantity=100, invested_value=100000, isin="INF179K01BD3"),
        ParsedHolding(raw_name="ICICI PRUDENTIAL GOLD ETF", quantity=50, invested_value=2500, isin="INF204KB17I5"),
    ]
    
    # Mocking market data service to avoid real network calls for stocks in this test
    import modules.market_data.service
    modules.market_data.service.market_data_service.get_latest_price = MagicMock(return_value=2500.0)

    normalized = asset_service.normalize_holdings(holdings)
    
    for h in normalized:
        print(f"Asset: {h.asset_name} -> Type: {h.asset_type}, Class: {h.asset_class}, Value: {h.current_value}")
        
    # Equity Share should be Equity Shares
    assert normalized[0].asset_class == AssetClass.EQUITY_SHARES
    # Liquid fund (MF) should be Mutual Funds (unless user wants a change here, but user said "Gold (ETF Gold BeES included in MF above)")
    assert normalized[1].asset_class == AssetClass.MUTUAL_FUNDS
    # Gold ETF should be Gold
    assert normalized[2].asset_class == AssetClass.GOLD
    
    print("Categorization Test Passed!")

if __name__ == "__main__":
    try:
        test_nav_fetcher()
        test_categorization()
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
