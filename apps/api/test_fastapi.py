from fastapi.testclient import TestClient
from main import app
import sys
import traceback

client = TestClient(app)

try:
    with client:
        response = client.post("/api/auth/register", json={
            "email": "testclient@example.com",
            "password": "password123"
        })
        print(response.status_code)
        print(response.json())
except Exception as e:
    traceback.print_exc()
