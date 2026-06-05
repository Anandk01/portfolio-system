import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "portfolio_ai"

async def inspect_portfolio():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["portfolios"]
    
    # Find the user's portfolio
    portfolio = await collection.find_one({"user_id": "6989daf8e18cd2d0a80ccdf0"})
    
    if not portfolio:
        print("No portfolio found")
        return
    
    print(f"\n{'='*80}")
    print(f"PORTFOLIO INSPECTION")
    print(f"{'='*80}\n")
    
    print(f"Total Holdings: {len(portfolio.get('holdings', []))}\n")
    
    # Group by asset type
    type_breakdown = {}
    type_value_breakdown = {}
    
    for idx, holding in enumerate(portfolio.get('holdings', [])):
        asset_type = holding.get('asset_type', 'UNKNOWN')
        asset_name = holding.get('asset_name', 'Unknown')
        current_value = holding.get('current_value', 0)
        
        if asset_type not in type_breakdown:
            type_breakdown[asset_type] = []
            type_value_breakdown[asset_type] = 0
        
        type_breakdown[asset_type].append({
            'name': asset_name,
            'value': current_value
        })
        type_value_breakdown[asset_type] += current_value
        
        print(f"{idx+1}. {asset_name}")
        print(f"   Type: {asset_type}")
        print(f"   Value: ₹{current_value:,.2f}\n")
    
    print(f"\n{'='*80}")
    print(f"ALLOCATION BY ASSET TYPE")
    print(f"{'='*80}\n")
    
    total_value = sum(type_value_breakdown.values())
    
    for asset_type, value in sorted(type_value_breakdown.items(), key=lambda x: x[1], reverse=True):
        percentage = (value / total_value * 100) if total_value > 0 else 0
        print(f"{asset_type}: ₹{value:,.2f} ({percentage:.2f}%)")
        print(f"  Holdings: {len(type_breakdown[asset_type])}")
        for h in type_breakdown[asset_type]:
            print(f"    - {h['name']}: ₹{h['value']:,.2f}")
        print()
    
    print(f"\nTotal Portfolio Value: ₹{total_value:,.2f}")
    
    # Check persisted allocation
    print(f"\n{'='*80}")
    print(f"PERSISTED ALLOCATION DATA")
    print(f"{'='*80}\n")
    
    if 'allocation' in portfolio:
        for item in portfolio['allocation']:
            print(f"{item['name']}: ₹{item['value']:,.2f}")

if __name__ == "__main__":
    asyncio.run(inspect_portfolio())
