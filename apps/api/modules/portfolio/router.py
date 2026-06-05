from fastapi import APIRouter, Depends, HTTPException
from typing import List
from modules.auth.router import get_current_user
from core.database import get_engine
from core.models import Portfolio, NormalizedHolding, ParsedPortfolio, AssetType, AccountType
from pydantic import BaseModel
from modules.analytics.service import analytics_engine
from modules.ai_insights.service import ai_insights_engine
import pandas as pd

router = APIRouter()

class SavePortfolioRequest(BaseModel):
    holdings: List[NormalizedHolding]

class SaveParsedRequest(BaseModel):
    """Request to save normalized holdings to ParsedPortfolio"""
    holdings: List[NormalizedHolding]

@router.get("/current")
async def get_current_portfolio(current_user = Depends(get_current_user)):
    """
    Fetch the user's current portfolio with persisted analytics and AI insights.
    """
    try:
        engine = get_engine()
        portfolio = await engine.find_one(Portfolio, Portfolio.user_id == current_user.id)
        
        if not portfolio:
            return {
                "holdings": [],
                "portfolio_metrics": None,
                "allocation_breakdown": [],
                "ai_strategy": None,
                "message": "No portfolio found. Please upload a statement."
            }
        
        # Use persisted results if they exist, otherwise compute basic fallbacks
        metrics = portfolio.metrics
        allocation_list = portfolio.allocation
        ai_strategy = portfolio.ai_strategy

        if metrics is None or not allocation_list:
            # Fallback to básica info if not yet processed
            metrics = analytics_engine.calculate_portfolio_metrics(portfolio.holdings, {})
            
            allocation_breakdown = {}
            for h in portfolio.holdings:
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
            
            opt = ai_insights_engine.optimize_portfolio_rl(portfolio.holdings)
            ins = ai_insights_engine.generate_explainable_insights(metrics)
            ai_strategy = {"optimization": opt, "insights": ins}

        return {
            "holdings": [h.model_dump() for h in portfolio.holdings],
            "portfolio_metrics": metrics,
            "allocation_breakdown": allocation_list,
            "ai_strategy": ai_strategy,
            "created_at": portfolio.created_at.isoformat()
        }
    except Exception as e:
        import traceback
        print(f"ERROR in get_current_portfolio: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_portfolio(request: SavePortfolioRequest, current_user = Depends(get_current_user)):
    """
    Save or update the user's portfolio holdings.
    """
    engine = get_engine()
    
    # Find existing portfolio or create new
    portfolio = await engine.find_one(Portfolio, Portfolio.user_id == current_user.id)
    
    if portfolio:
        # Update existing
        portfolio.holdings = request.holdings
        await engine.save(portfolio)
    else:
        # Create new
        portfolio = Portfolio(
            user_id=current_user.id,
            holdings=request.holdings
        )
        await engine.save(portfolio)
    
    return {
        "status": "success",
        "holdings_count": len(request.holdings),
        "message": "Portfolio saved successfully"
    }

@router.post("/save-parsed")
async def save_parsed_holdings(request: SaveParsedRequest, current_user = Depends(get_current_user)):
    """
    Save normalized holdings to ParsedPortfolio collection for review.
    """
    engine = get_engine()
    
    # Fetch existing parsed portfolio
    parsed_portfolio = await engine.find_one(ParsedPortfolio, ParsedPortfolio.user_id == current_user.id)
    
    if not parsed_portfolio:
        raise HTTPException(status_code=404, detail="No parsed portfolio found. Please upload a PDF first.")
    
    # Update with normalized holdings
    parsed_portfolio.holdings = request.holdings
    await engine.save(parsed_portfolio)
    
    return {
        "status": "success",
        "message": "Normalized holdings saved for review"
    }

@router.post("/process")
async def process_portfolio(current_user = Depends(get_current_user)):
    """
    Process parsed portfolio: normalize → fetch market data → compute analytics.
    This is called after user reviews and approves the parsed holdings.
    """
    from modules.asset_resolver.service import asset_service
    from modules.analytics.service import analytics_engine
    from modules.ai_insights.service import ai_insights_engine
    from modules.market_data.service import market_data_service
    
    engine = get_engine()
    
    # Fetch parsed portfolio
    parsed_portfolio = await engine.find_one(
        ParsedPortfolio, 
        ParsedPortfolio.user_id == current_user.id
    )
    
    if not parsed_portfolio:
        raise HTTPException(status_code=404, detail="No parsed portfolio found. Please upload a PDF first.")
    
    if parsed_portfolio.status == "processing":
        raise HTTPException(status_code=409, detail="Portfolio is already being processed")
    
    try:
        # Update status to processing
        parsed_portfolio.status = "processing"
        await engine.save(parsed_portfolio)
        
        # Step 1: Normalize holdings (resolve ISINs, fetch metadata)
        # Note: holdings are already normalized in the /save-parsed step
        
        if not parsed_portfolio.holdings or len(parsed_portfolio.holdings) == 0:
            raise HTTPException(
                status_code=400, 
                detail="No holdings to process. Please re-upload your PDF."
            )
        
        normalized_holdings = parsed_portfolio.holdings
        
        # Step 2: Fetch Market Data for Analytics
        market_data_map = {}
        for h in normalized_holdings:
            if h.symbol:
                try:
                    # Fetch 2y historical data for each symbol
                    file_path = market_data_service.fetch_historical_data(h.symbol)
                    market_data_map[h.symbol] = pd.read_parquet(file_path)
                    print(f"DEBUG: Loaded market data for {h.symbol}, shape: {market_data_map[h.symbol].shape}")
                except Exception as e:
                    print(f"Warning: Could not fetch market data for {h.symbol}: {e}")
        
        print(f"DEBUG: Total symbols with market data: {len(market_data_map)}")
        
        # Step 3: Compute analytics & insights before saving
        metrics = analytics_engine.calculate_portfolio_metrics(normalized_holdings, market_data_map)
        
        allocation_breakdown = {}
        for h in normalized_holdings:
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
        
        ai_optimization = ai_insights_engine.optimize_portfolio_rl(normalized_holdings)
        ai_insights = ai_insights_engine.generate_explainable_insights(metrics)
        ai_strategy = {
            "optimization": ai_optimization,
            "insights": ai_insights
        }

        # Step 4: Save to permanent portfolio collection
        portfolio = await engine.find_one(Portfolio, Portfolio.user_id == current_user.id)
        
        if portfolio:
            portfolio.holdings = normalized_holdings
            portfolio.metrics = metrics
            portfolio.allocation = allocation_list
            portfolio.ai_strategy = ai_strategy
            await engine.save(portfolio)
        else:
            portfolio = Portfolio(
                user_id=current_user.id,
                holdings=normalized_holdings,
                metrics=metrics,
                allocation=allocation_list,
                ai_strategy=ai_strategy
            )
            await engine.save(portfolio)
        
        
        # Update parsed portfolio status
        parsed_portfolio.status = "completed"
        await engine.save(parsed_portfolio)
        
        return {
            "status": "processed",
            "holdings_count": len(normalized_holdings),
            "portfolio_metrics": metrics,
            "allocation_breakdown": allocation_list,
            "ai_strategy": ai_strategy,
            "message": "Portfolio processed successfully"
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR in process_portfolio: {str(e)}")
        traceback.print_exc()
        
        # Update status to failed
        parsed_portfolio.status = "failed"
        await engine.save(parsed_portfolio)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.delete("/clear")
async def clear_portfolio(current_user = Depends(get_current_user)):
    """
    Clear the user's portfolio.
    """
    engine = get_engine()
    portfolio = await engine.find_one(Portfolio, Portfolio.user_id == current_user.id)
    
    if portfolio:
        await engine.delete(portfolio)
        return {"status": "success", "message": "Portfolio cleared"}
    
    return {"status": "success", "message": "No portfolio to clear"}
