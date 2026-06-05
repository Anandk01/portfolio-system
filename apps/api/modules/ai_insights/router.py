from fastapi import APIRouter, Depends
from typing import List
from .service import ai_insights_engine
from modules.auth.router import get_current_user
from core.models import NormalizedHolding

router = APIRouter()

@router.post("/optimize")
async def optimize_portfolio(holdings: List[NormalizedHolding], current_user = Depends(get_current_user)):
    """
    Get RL-based portfolio optimization suggestions.
    """
    return ai_insights_engine.optimize_portfolio_rl(holdings)

@router.get("/explain")
async def get_explanations(current_user = Depends(get_current_user)):
    """
    Get explainable AI text insights.
    """
    # In a real app, we'd pass performance data here
    return ai_insights_engine.generate_explainable_insights({})
