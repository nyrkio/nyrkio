#!/usr/bin/env python3
"""Test with john@foo.com user"""
import requests
import json

# Login with john@foo.com
print("Logging in with john@foo.com...")
login_response = requests.post(
    "http://localhost:8001/api/v0/auth/jwt/login",
    data={"username": "john@foo.com", "password": "foo"}
)
print(f"Login status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Got token: {token[:30]}...")

# Try to create result
print("\nCreating result...")
result_data = [
    {
        "timestamp": 1,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"}
        ],
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "main",
            "git_commit": "123456"
        }
    }
]

result_response = requests.post(
    "http://localhost:8001/api/v0/result/test-john",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json=result_data
)

print(f"Result status: {result_response.status_code}")
print(f"Response: {result_response.text[:500]}")
