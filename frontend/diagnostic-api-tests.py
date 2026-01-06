#!/usr/bin/env python3
"""
Diagnostic API Test Suite
Compares different scenarios to isolate the backend crash
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_login(email, password):
    """Test login and return token"""
    print(f"\n[TEST] Login with {email}")
    response = requests.post(
        f"{BASE_URL}/api/v0/auth/jwt/login",
        data={"username": email, "password": password}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"  ✓ Got token")
        return token
    else:
        print(f"  ✗ Failed: {response.text}")
        return None

def test_create_result(token, test_name, data):
    """Test creating a result"""
    print(f"\n[TEST] Create result: {test_name}")
    print(f"  Data: {json.dumps(data, indent=2)[:200]}...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/result/{test_name}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=10
        )
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print(f"  ✓ SUCCESS")
            return True
        else:
            print(f"  ✗ FAILED")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"  ✗ EXCEPTION: {type(e).__name__}: {e}")
        return False

def main():
    print_section("DIAGNOSTIC API TEST SUITE")

    # Test 1: Simple minimal data
    print_section("Test 1: Minimal Valid Data")
    token = test_login("john@foo.com", "foo")
    if token:
        minimal_data = [
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
        test_create_result(token, "diagnostic-test-1", minimal_data)

    # Test 2: With multiple metrics (like backend test)
    print_section("Test 2: Multiple Metrics (Backend Test Format)")
    if token:
        multi_metric_data = [
            {
                "timestamp": 1,
                "metrics": [
                    {"name": "metric1", "value": 1.0, "unit": "ms"},
                    {"name": "metric2", "value": 2.0, "unit": "ms"}
                ],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "main",
                    "git_commit": "123456"
                }
            }
        ]
        test_create_result(token, "diagnostic-test-2", multi_metric_data)

    # Test 3: Multiple timestamps
    print_section("Test 3: Multiple Timestamps")
    if token:
        multi_time_data = [
            {
                "timestamp": 1,
                "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "main",
                    "git_commit": "123456"
                }
            },
            {
                "timestamp": 2,
                "metrics": [{"name": "metric1", "value": 2.0, "unit": "ms"}],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "main",
                    "git_commit": "123456"
                }
            }
        ]
        test_create_result(token, "diagnostic-test-3", multi_time_data)

    # Test 4: With extra_info
    print_section("Test 4: With Extra Info")
    if token:
        extra_info_data = [
            {
                "timestamp": 1,
                "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "main",
                    "git_commit": "123456"
                },
                "extra_info": {"foo": "bar"}
            }
        ]
        test_create_result(token, "diagnostic-test-4", extra_info_data)

    # Test 5: Different branch names
    print_section("Test 5: Different Branch Name (ui-testing)")
    if token:
        branch_data = [
            {
                "timestamp": 1,
                "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "ui-testing",  # Different branch
                    "git_commit": "test123"
                }
            }
        ]
        test_create_result(token, "diagnostic-test-5", branch_data)

    # Test 6: With test@example.com user
    print_section("Test 6: With test@example.com User")
    token2 = test_login("test@example.com", "testpassword123")
    if token2:
        test_create_result(token2, "diagnostic-test-6", minimal_data)

    # Test 7: Very long test name with slashes
    print_section("Test 7: Test Name With Slashes")
    if token:
        test_create_result(token, "org/repo/branch/test-name", minimal_data)

    # Test 8: Current timestamp
    print_section("Test 8: Current Timestamp")
    if token:
        import time
        current_time_data = [
            {
                "timestamp": int(time.time()),
                "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
                "attributes": {
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                    "branch": "main",
                    "git_commit": "123456"
                }
            }
        ]
        test_create_result(token, "diagnostic-test-8", current_time_data)

    print_section("TEST SUITE COMPLETE")

if __name__ == "__main__":
    main()
