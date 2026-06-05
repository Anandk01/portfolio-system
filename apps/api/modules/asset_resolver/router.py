from fastapi import APIRouter, HTTPException
from typing import List
from core.models import ParsedHolding
from .service import asset_service

router = APIRouter()

@router.post("/normalize")
async def normalize_holdings(holdings: List[ParsedHolding]):
    """
    Module 2: Asset Resolver
    Normalize raw extracted holdings.
    """
    try:
        # In a real scenario, we'd use Pydantic models here
        normalized = asset_service.normalize_holdings(holdings)
        return {"normalized_holdings": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")
