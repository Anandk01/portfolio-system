from fastapi import APIRouter, HTTPException
from .service import market_data_service

router = APIRouter()

@router.get("/historical/{symbol}")
async def get_historical_data(symbol: str):
    """
    Module 3: Market Data
    Fetch historical data for a symbol.
    """
    try:
        file_path = market_data_service.fetch_historical_data(symbol)
        return {"symbol": symbol, "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price/{symbol}")
async def get_latest_price(symbol: str):
    """
    Get latest price for a symbol.
    """
    try:
        price = market_data_service.get_latest_price(symbol)
        return {"symbol": symbol, "price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
