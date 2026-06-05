
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Using standard loopback for connection
MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "portfolio_ai"

async def fix_asset_classes():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["portfolios"]
    
    print("Scanning portfolios for invalid asset classes...")
    
    # Update 'Equity' -> 'Equity Shares'
    result = await collection.update_many(
        {"holdings.asset_class": "Equity"},
        {"$set": {"holdings.$[elem].asset_class": "Equity Shares"}},
        array_filters=[{"elem.asset_class": "Equity"}]
    )
    
    print(f"Updated {result.modified_count} portfolios (Equity -> Equity Shares)")

    # Also checkParsedPortfolios
    parsed_collection = db["parsed_portfolios"]
    result_parsed = await parsed_collection.update_many(
        {"holdings.asset_class": "Equity"},
        {"$set": {"holdings.$[elem].asset_class": "Equity Shares"}},
        array_filters=[{"elem.asset_class": "Equity"}]
    )
    print(f"Updated {result_parsed.modified_count} parsed portfolios (Equity -> Equity Shares)")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fix_asset_classes())
