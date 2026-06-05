import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def reproduce():
    import time
    email = f"test_{int(time.time())}@example.com"
    password = "password123"

    # 1. Register
    print(f"Registering {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password
    })
    if resp.status_code not in [200, 400]: # 400 is fine if already exists
        print(f"Registration failed: {resp.status_code} {resp.text}")
        return

    # 2. Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("Login successful. Got token.")
        
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Seed Data
        print("Seeding portfolio data...")
        holdings = [
            {
                "symbol": "AAPL",
                "isin": "US0378331005",
                "asset_name": "Apple Inc.",  # Changed from name to asset_name
                "quantity": 10.0,
                "buy_price": 150.0,
                "current_price": 180.0,
                "invested_value": 1500.0,    # Added invested_value
                "current_value": 1800.0,
                "asset_type": "STOCK",       # Added asset_type
                "asset_class": "Equity Shares", # Fixed enum value
                "sector": "Technology"
            },
            {
                "symbol": "INFY.NS",
                "isin": "INE009A01021",
                "asset_name": "Infosys Limited", # Changed from name to asset_name
                "quantity": 50.0,
                "buy_price": 1400.0,
                "current_price": 1600.0,
                "invested_value": 70000.0,   # Added invested_value
                "current_value": 80000.0,
                "asset_type": "STOCK",       # Added asset_type
                "asset_class": "Equity Shares", # Fixed enum value
                "sector": "Technology"
            }
        ]
        resp = requests.post(f"{BASE_URL}/portfolio/save", json={"holdings": holdings}, headers=headers)
        if resp.status_code != 200:
             print(f"Seeding failed: {resp.status_code} {resp.text}")
             return

        # 4. Trigger Error
        print("Requesting portfolio...")
        resp = requests.get(f"{BASE_URL}/portfolio/current", headers=headers)
        
        print(f"Portfolio Request Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    reproduce()
