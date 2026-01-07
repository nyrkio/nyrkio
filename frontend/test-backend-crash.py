#!/usr/bin/env python3
"""
Minimal test to reproduce backend crash when creating test results.
This will help identify the root cause of the 500 error.
"""
import requests
import json
import sys

print("=" * 80)
print("BACKEND CRASH REPRODUCTION TEST")
print("=" * 80)

# Step 1: Login
print("\n[Step 1] Logging in...")
try:
    login_response = requests.post(
        "http://localhost:8001/api/v0/auth/jwt/login",
        data={"username": "test@example.com", "password": "testpassword123"},
        timeout=5
    )
    print(f"  ✓ Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print(f"  ✗ Login failed: {login_response.text}")
        sys.exit(1)

    token = login_response.json()["access_token"]
    print(f"  ✓ Got token: {token[:30]}...")
except Exception as e:
    print(f"  ✗ Login error: {e}")
    sys.exit(1)

# Step 2: Verify user info
print("\n[Step 2] Verifying authenticated user...")
try:
    user_response = requests.get(
        "http://localhost:8001/api/v0/users/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    print(f"  ✓ User info status: {user_response.status_code}")
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"  ✓ User email: {user_data.get('email')}")
        print(f"  ✓ User ID: {user_data.get('id')}")
except Exception as e:
    print(f"  ✗ User info error: {e}")

# Step 3: Try to create a minimal test result
print("\n[Step 3] Creating minimal test result...")

test_name = "crash-test-minimal"

# Minimal valid data based on backend test examples
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

print(f"\n  Request URL: POST http://localhost:8001/api/v0/result/{test_name}")
print(f"  Request Headers:")
print(f"    Authorization: Bearer {token[:20]}...")
print(f"    Content-Type: application/json")
print(f"\n  Request Body:")
print(json.dumps(result_data, indent=4))

try:
    result_response = requests.post(
        f"http://localhost:8001/api/v0/result/{test_name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=result_data,
        timeout=10
    )

    print(f"\n  Response Status: {result_response.status_code}")
    print(f"  Response Headers: {dict(result_response.headers)}")
    print(f"\n  Response Body:")

    try:
        response_json = result_response.json()
        print(json.dumps(response_json, indent=4))
    except:
        print(result_response.text)

    if result_response.status_code == 200:
        print("\n  ✓ SUCCESS! Result created successfully")
    else:
        print(f"\n  ✗ FAILED with status {result_response.status_code}")

except requests.exceptions.ConnectionError as e:
    print(f"\n  ✗ CONNECTION ERROR: {e}")
    print("     Backend may have crashed!")
except requests.exceptions.Timeout as e:
    print(f"\n  ✗ TIMEOUT: {e}")
    print("     Backend may be stuck!")
except Exception as e:
    print(f"\n  ✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")

# Step 4: Check if backend is still responsive
print("\n[Step 4] Checking if backend is still responsive...")
try:
    health_response = requests.get("http://localhost:8001/docs", timeout=3)
    if health_response.status_code == 200:
        print("  ✓ Backend is still responding to requests")
    else:
        print(f"  ? Backend returned status {health_response.status_code}")
except Exception as e:
    print(f"  ✗ Backend is not responding: {e}")
    print("     Backend likely crashed!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
