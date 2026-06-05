
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
import pandas as pd
from core.models import NormalizedHolding
from .service import analytics_engine, sentiment_service, PricePredictor
from .score_service import score_service
from .benchmark_service import benchmark_service
from modules.market_data.service import market_data_service
from modules.auth.router import get_current_user

router = APIRouter()

class BenchmarkRequest(BaseModel):
    holdings: Optional[List[NormalizedHolding]] = None

@router.post("/metrics")
async def calculate_metrics(holdings: List[NormalizedHolding]):
    """
    Module 4: Analytics
    Calculate portfolio metrics using real market data.
    """
    try:
        market_data_map = {}
        for h in holdings:
            symbol = h.symbol
            if symbol and not symbol.endswith(".UNRESOLVED"):
                # Defensive check for clearly malformed symbols (e.g., from stale frontend data)
                # ISIN is 12 chars. Symbol is usually < 12. Combined is > 15.
                if len(symbol) > 15 and re.search(r'[A-Z]{2}[0-9]{2}', symbol):
                    print(f"Skipping malformed symbol: {symbol}")
                    continue
                    
                try:
                    parquet_path = market_data_service.fetch_historical_data(symbol)
                    df = pd.read_parquet(parquet_path)
                    market_data_map[h.symbol] = df
                except Exception as e:
                    print(f"Warning: Could not fetch market data for {h.symbol}: {e}")
        
        metrics = analytics_engine.calculate_portfolio_metrics(holdings, market_data_map)
        return {
            "portfolio_metrics": metrics,
            "asset_analysis": [] # Placeholder for future expansion
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/score")
async def get_portfolio_score(user=Depends(get_current_user)):
    """
    Get AI Portfolio Health Score (0-100) and Grade.
    """
    # 0. Dependencies
    from modules.portfolio.service import portfolio_service

    try:
        # 1. Fetch Portfolio
        portfolio = await portfolio_service.get_portfolio(user.id)
        if not portfolio or not portfolio.holdings:
            return score_service._empty_score()
        
        # 2. Get Market Data Map
        market_data_map = {}
        for h in portfolio.holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(path)
                except Exception:
                    pass

        # 3. Calculate Base Metrics
        # Ensure analytics_engine doesn't crash on empty or partial data
        metrics = analytics_engine.calculate_portfolio_metrics(portfolio.holdings, market_data_map)
        
        # 4. Calculate Score
        score_data = score_service.calculate_health_score(portfolio, metrics)
        return score_data
    except Exception as e:
        print(f"Error calculating score: {e}")
        import traceback
        traceback.print_exc()
        return score_service._empty_score()


@router.post("/benchmark")
async def get_benchmark_comparison(request: Optional[BenchmarkRequest] = None, period: str = "1y", user=Depends(get_current_user)):
    """
    Get Portfolio vs NIFTY 50 vs Gold comparison.
    If holdings is provided, simulates that specific portfolio's performance.
    """
    from modules.portfolio.service import portfolio_service
    from .benchmark_service import benchmark_service
    
    try:
        # 1. Get Holdings (Simulated or Current)
        holdings = request.holdings if request else None
        
        if holdings is None:
            portfolio = await portfolio_service.get_portfolio(user.id)
            if not portfolio: return []
            holdings = portfolio.holdings

        if not holdings: return []

        # 2. Get Dates and Market Data
        market_data_map = {}
        for h in holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    path = market_data_service.fetch_historical_data(h.symbol, period="2y") # Fetch enough history
                    market_data_map[h.symbol] = pd.read_parquet(path)
                except Exception:
                    pass

        # 3. Calculate Portfolio Historical Returns
        pf_returns = analytics_engine.calculate_historical_returns(holdings, market_data_map)
        
        # 4. Compare with benchmarks for the requested period
        chart_data = benchmark_service.get_benchmark_comparison(pf_returns, period=period)
        return chart_data
        
    except Exception as e:
        print(f"Error generating benchmark: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.post("/simulate")
async def simulate_portfolio(holdings: List[NormalizedHolding], user=Depends(get_current_user)):
    """
    Simulate portfolio metrics for 'What-If' scenarios.
    Does NOT save to database.
    """
    try:
        # 1. Fetch Market Data for Hypothetical Holdings
        # We need to fetch data even for new assets the user might be testing
        market_data_map = {}
        for h in holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    # Try to get data. If not in cache, it might be slow, but acceptable for simulation.
                    # For MVP, we assume commonly traded assets or already cached ones.
                    path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(path)
                except Exception:
                    pass

        # 2. Calculate Metrics
        metrics = analytics_engine.calculate_portfolio_metrics(holdings, market_data_map)
        
        # 3. Calculate Allocation Breakdown (Duplicate logic from portfolio router for consistency)
        from core.models import AssetType, AccountType
        allocation_breakdown = {}
        for h in holdings:
            if h.asset_type == AssetType.STOCK:
                label = "Equity"
            elif (h.asset_type == AssetType.MF and h.account_type == AccountType.DEMAT) or h.asset_type == AssetType.ETF:
                label = "Mutual Funds (Demat)"
            elif h.asset_type == AssetType.MF and h.account_type == AccountType.SOA:
                label = "Mutual Funds (SOA)"
            else:
                type_label_map = {
                    AssetType.COMMODITY: "Commodities",
                    AssetType.CASH: "Cash",
                }
                label = type_label_map.get(h.asset_type, "Others")
                
            allocation_breakdown[label] = allocation_breakdown.get(label, 0) + h.current_value
        
        allocation_list = [{"name": k, "value": round(v, 2)} for k, v in allocation_breakdown.items()]

        # 4. Calculate Score (Optional, but good for comparison)
        # We need a dummy portfolio object to pass to score_service
        from core.models import Portfolio
        dummy_pf = Portfolio(user_id="sim", email="sim", holdings=holdings)
        score_data = score_service.calculate_health_score(dummy_pf, metrics)
        
        return {
            "metrics": metrics,
            "score": score_data,
            "allocation": allocation_list
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/correlation")
async def get_risk_analysis(holdings: List[NormalizedHolding], user=Depends(get_current_user)):
    """
    Get Correlation Matrix and Drawdown Analysis.
    Strategies:
    - Log Returns correlation matrix.
    - Max Drawdown calculation.
    """
    from .risk_service import risk_service
    
    try:
        if not holdings: return {}

        # 1. Fetch Data
        market_data_map = {}
        for h in holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(path)
                except Exception:
                    pass

        # 2. Calculate Returns Matrix (Reuse helper but need raw DF)
        # We need a DataFrame where columns are symbols and rows are daily returns
        # Reusing calculate_historical_returns logic roughly
        
        # Extract basic returns dataframe for correlation
        returns_df = pd.DataFrame()
        for sym, df in market_data_map.items():
            if "Close" in df.columns:
                # Align on Date if possible
                if "Date" in df.columns: df = df.set_index("Date")
                rets = df["Close"].pct_change()
                returns_df[sym] = rets
        
        # Align
        if not returns_df.empty:
            returns_df = returns_df.ffill().fillna(0)

        # 3. Correlation Metrics
        risk_data = risk_service.calculate_risk_metrics(returns_df)

        # 4. Portfolio Drawdown
        # We need weighted portfolio returns series
        pf_returns = analytics_engine.calculate_historical_returns(holdings, market_data_map)
        dd_data = risk_service.calculate_portfolio_drawdown(pf_returns)

        return {
            "correlation": risk_data,
            "drawdown": dd_data
        }

    except Exception as e:
        print(f"Error in risk analysis: {e}")
        raise HTTPException(status_code=500, detail="Risk analysis failed")


@router.post("/optimize")
async def optimize_portfolio(
    holdings: List[NormalizedHolding], 
    strategy: str = "aggressive",
    user=Depends(get_current_user)
):
    """
    AI Optimization using SciPy Efficient Frontier.
    Strategies: 'aggressive' (Max Sharpe) or 'conservative' (Min Vol).
    """
    from .optimization_service import optimization_service
    
    try:
        # 1. Fetch Data
        market_data_map = {}
        current_weights = {}
        total_val = sum(h.current_value for h in holdings)
        
        for h in holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(path)
                    
                    if total_val > 0:
                        current_weights[h.symbol] = h.current_value / total_val
                except Exception:
                    pass

        # 2. Prepare Returns DataFrame
        returns_df = pd.DataFrame()
        for sym, df in market_data_map.items():
            if "Close" in df.columns:
                if "Date" in df.columns: df = df.set_index("Date")
                rets = df["Close"].pct_change()
                returns_df[sym] = rets
        
        if not returns_df.empty:
            returns_df = returns_df.ffill().fillna(0) # Align

        # 3. Optimize
        result = optimization_service.optimize_portfolio(returns_df, current_weights, strategy)
        
        return result

    except Exception as e:
        print(f"Error in optimization: {e}")
    except Exception as e:
        print(f"Error in optimization: {e}")
        raise HTTPException(status_code=500, detail="Optimization failed")


@router.post("/frontier")
async def get_efficient_frontier(holdings: List[NormalizedHolding], user=Depends(get_current_user)):
    """
    Generate Efficient Frontier via Monte Carlo (n=1000).
    """
    from .optimization_service import optimization_service
    
    try:
        # 1. Fetch Data
        market_data_map = {}
        current_weights = {}
        total_val = sum(h.current_value for h in holdings)
        
        for h in holdings:
            if h.symbol and h.symbol != "Unresolved":
                try:
                    path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(path)
                    
                    if total_val > 0:
                        current_weights[h.symbol] = h.current_value / total_val
                except Exception:
                    pass

        # 2. Prepare Returns DataFrame
        returns_df = pd.DataFrame()
        for sym, df in market_data_map.items():
            if "Close" in df.columns:
                if "Date" in df.columns: df = df.set_index("Date")
                rets = df["Close"].pct_change()
                returns_df[sym] = rets
        
        if not returns_df.empty:
            returns_df = returns_df.ffill().fillna(0)

        # 3. Simulate
        result = optimization_service.generate_efficient_frontier(returns_df, current_weights)
        return result

    except Exception as e:
        print(f"Error generating frontier: {e}")
        raise HTTPException(status_code=500, detail="Frontier generation failed")
