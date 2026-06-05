
import asyncio
import sys

print("Starting debug_users.py...")

try:
    from core.database import init_db, get_engine
    from core.models import User
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

async def list_users():
    print("Initializing DB...")
    await init_db()
    print("DB Initialized. Getting engine...")
    engine = get_engine()
    print("Engine obtained. Querying users...")
    users = await engine.find(User)
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"- {user.email} (ID: {user.id})")

if __name__ == "__main__":
    asyncio.run(list_users())
