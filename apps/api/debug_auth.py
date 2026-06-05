
import asyncio
import sys

# Add current directory to path
sys.path.append(".")

from core.database import init_db, get_engine
from core.models import User
from modules.auth.router import pwd_context, verify_password, get_password_hash

async def debug_auth(email, password):
    print(f"Initializing DB...")
    await init_db()
    engine = get_engine()
    
    print(f"Finding user {email}...")
    user = await engine.find_one(User, User.email == email)
    
    if not user:
        print(f"User {email} not found!")
        return
    
    print(f"User ID: {user.id}")
    print(f"Stored Hash: {user.hashed_password}")
    
    # Try verifying
    is_valid = verify_password(password, user.hashed_password)
    print(f"Verification check for '{password}': {is_valid}")
    
    if not is_valid:
        print("Verification FAILED. Resetting password again...")
        new_hash = get_password_hash(password)
        print(f"New Hash: {new_hash}")
        user.hashed_password = new_hash
        await engine.save(user)
        print("Password saved.")
        
        # Verify again
        is_valid_now = verify_password(password, new_hash)
        print(f"Immediate verification check: {is_valid_now}")
    else:
        print("Verification SUCCEEDED. The password in DB is correct.")

if __name__ == "__main__":
    asyncio.run(debug_auth("a@gmail.com", "password123"))
