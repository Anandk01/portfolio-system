from fastapi import APIRouter, HTTPException, Depends
from typing import List
from modules.auth.router import get_current_user
from modules.portfolio.service import portfolio_service
from .feed_service import feed_service
from .schemas import FeedResponse

router = APIRouter()

@router.get("/feed", response_model=FeedResponse)
async def get_intelligence_feed(user=Depends(get_current_user)):
    """
    Get AI Intelligence Feed:
    - Recent Price Signals
    - News Sentiment Analysis (FinBERT)
    - Risk/Concentration Alerts
    """
    try:
        portfolio = await portfolio_service.get_portfolio(user.id)
        if not portfolio:
            from datetime import datetime
            return {"items": [], "generated_at": datetime.now()}
        
        items = await feed_service.generate_feed(portfolio)
        
        from datetime import datetime
        return {
            "items": items,
            "generated_at": datetime.now()
        }
    except Exception as e:
        print(f"Error generating feed: {e}")
        import traceback
        traceback.print_exc()
        from datetime import datetime
        return {"items": [], "generated_at": datetime.now()}
