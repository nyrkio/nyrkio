#!/usr/bin/env python3
import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8001/api/v0/auth/jwt/login",
    data={"username": "test@example.com", "password": "testpassword123"}
)
print(f"Login status: {login_response.status_code}")
token = login_response.json()["access_token"]
print(f"Got token: {token[:20]}...")

# Create result
result_data = [
    {
        "timestamp": 1700000000,
        "metrics": [
            {
                "name": "test-api-python",
                "value": 100.5,
                "unit": "ms"
            }
        ],
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "ui-testing",
            "git_commit": "test123"
        }
    }
]

print(f"\nSending data: {json.dumps(result_data, indent=2)}")

result_response = requests.post(
    "http://localhost:8001/api/v0/result/test-api-python",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json=result_data
)

print(f"\nResult creation status: {result_response.status_code}")
print(f"Response: {result_response.text}")
