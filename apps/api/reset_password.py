
import asyncio
import sys

# Add current directory to path so we can import modules
sys.path.append(".")

from core.database import init_db, get_engine
from core.models import User
from modules.auth.router import get_password_hash

async def reset_password(email, new_password):
    print(f"Initializing DB...")
    await init_db()
    engine = get_engine()
    
    print(f"Finding user {email}...")
    user = await engine.find_one(User, User.email == email)
    
    if not user:
        print(f"User {email} not found!")
        return
    
    print(f"User found. Resetting password to '{new_password}'...")
    hashed = get_password_hash(new_password)
    user.hashed_password = hashed
    
    await engine.save(user)
    print("Password updated successfully.")

if __name__ == "__main__":
    asyncio.run(reset_password("a@gmail.com", "password123"))
