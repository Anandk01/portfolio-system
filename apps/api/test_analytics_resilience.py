import pandas as pd
import numpy as np
from modules.analytics.service import analytics_engine
from modules.ai_insights.service import ai_insights_engine
from core.models import NormalizedHolding, AssetType, RiskCategory

def test_resilience():
    # 1. Mock Holdings: 1 Stock (with data), 1 ETF (with data), 1 MF (no data)
    holdings = [
        NormalizedHolding(
            symbol="RELIANCE.NS",
            asset_name="RELIANCE INDUSTRIES",
            asset_type=AssetType.STOCK,
            current_value=100000,
            quantity=40,
            invested_value=90000,
            risk_category=RiskCategory.MODERATE
        ),
        NormalizedHolding(
            symbol="NIFTYBEES.NS",
            asset_name="NIFTY BEES ETF",
            asset_type=AssetType.ETF,
            current_value=50000,
            quantity=200,
            invested_value=45000,
            risk_category=RiskCategory.LOW
        ),
        NormalizedHolding(
            symbol=None, # MF often lacks symbol
            asset_name="HDFC TOP 100 MF",
            asset_type=AssetType.MF,
            current_value=150000, # Largest holding
            quantity=1000,
            invested_value=120000,
            risk_category=RiskCategory.MODERATE
        )
    ]

    # 2. Mock Market Data (non-overlapping dates)
    dates_a = pd.date_range(start="2023-01-01", periods=10, freq="D")
    dates_b = pd.date_range(start="2023-01-05", periods=10, freq="D")
    
    market_data = {
        "RELIANCE.NS": pd.DataFrame({"Close": [100 + i for i in range(10)]}, index=dates_a),
        "NIFTYBEES.NS": pd.DataFrame({"Close": [50 + i*0.5 for i in range(10)]}, index=dates_b)
    }

    print("\n--- Testing Analytics Engine Resilience ---")
    metrics = analytics_engine.calculate_portfolio_metrics(holdings, market_data)
    
    print(f"Total Value (Expected 300,000): {metrics.get('total_value')}")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio')}")
    print(f"Volatility: {metrics.get('annual_volatility')}")
    print(f"Diversification: {metrics.get('diversification_score')}")

    print("\n--- Testing AI Insights Guardrails ---")
    insights = ai_insights_engine.generate_explainable_insights(metrics)
    for i in insights:
        print(f"Insight: {i}")

if __name__ == "__main__":
    # Add dummy Date column to match set_index logic in service
    import datetime
    test_resilience()
