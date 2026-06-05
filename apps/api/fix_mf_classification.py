import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "portfolio_ai"

async def reclassify_mutual_funds():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["portfolios"]
    
    print("Reclassifying mutual funds from ETF to MF...")
    
    # Update holdings where asset_name contains "MUTUAL FUND" but asset_type is ETF
    result = await collection.update_many(
        {
            "holdings": {
                "$elemMatch": {
                    "asset_name": {"$regex": "MUTUAL FUND", "$options": "i"},
                    "asset_type": "ETF"
                }
            }
        },
        {
            "$set": {
                "holdings.$[elem].asset_type": "MF"
            }
        },
        array_filters=[
            {
                "elem.asset_name": {"$regex": "MUTUAL FUND", "$options": "i"},
                "elem.asset_type": "ETF"
            }
        ]
    )
    
    print(f"Updated {result.modified_count} portfolios")
    
    # Also update parsed_portfolios
    parsed_collection = db["parsed_portfolios"]
    result_parsed = await parsed_collection.update_many(
        {
            "holdings": {
                "$elemMatch": {
                    "asset_name": {"$regex": "MUTUAL FUND", "$options": "i"},
                    "asset_type": "ETF"
                }
            }
        },
        {
            "$set": {
                "holdings.$[elem].asset_type": "MF"
            }
        },
        array_filters=[
            {
                "elem.asset_name": {"$regex": "MUTUAL FUND", "$options": "i"},
                "elem.asset_type": "ETF"
            }
        ]
    )
    
    print(f"Updated {result_parsed.modified_count} parsed portfolios")

if __name__ == "__main__":
    asyncio.run(reclassify_mutual_funds())
