import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "portfolio_ai"

async def update_allocation():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["portfolios"]
    
    # Find the user's portfolio
    portfolio = await collection.find_one({"user_id": "6989daf8e18cd2d0a80ccdf0"})
    
    if not portfolio:
        print("No portfolio found")
        return
    
    # Recalculate allocation based on asset_type
    allocation_breakdown = {}
    type_label_map = {
        "STOCK": "Stocks",
        "MF": "Mutual Funds",
        "ETF": "ETFs",
        "COMMODITY": "Commodities",
        "CASH": "Cash",
        "UNKNOWN": "Others"
    }
    
    for holding in portfolio.get('holdings', []):
        asset_type = holding.get('asset_type', 'UNKNOWN')
        label = type_label_map.get(asset_type, asset_type)
        current_value = holding.get('current_value', 0)
        allocation_breakdown[label] = allocation_breakdown.get(label, 0) + current_value
    
    allocation_list = [{"name": k, "value": round(v, 2)} for k, v in allocation_breakdown.items()]
    
    # Update the portfolio
    await collection.update_one(
        {"user_id": "6989daf8e18cd2d0a80ccdf0"},
        {"$set": {"allocation": allocation_list}}
    )
    
    print("Updated allocation:")
    for item in allocation_list:
        print(f"  {item['name']}: ₹{item['value']:,.2f}")

if __name__ == "__main__":
    asyncio.run(update_allocation())
