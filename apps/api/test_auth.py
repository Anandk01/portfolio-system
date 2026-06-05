import urllib.request
import json

req = urllib.request.Request(
    "http://localhost:8000/api/auth/register",
    data=json.dumps({"email": "test99@example.com", "password": "password123"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.status)
        print("Response Body:", response.read().decode())
except urllib.error.HTTPError as e:
    print("Status Code:", e.code)
    print("Response Body:", e.read().decode())
