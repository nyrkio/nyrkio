import asyncio
from datetime import datetime
from pprint import pprint
from typing import Dict, List

from backend.db.db import NULL_DATETIME, MockDBStrategy
from starlette.testclient import TestClient

from backend.api.api import app
from backend.api.changes import _build_result_series
from backend.api.public import extract_public_test_name

from backend.conftest import AuthenticatedTestClient, SuperuserClient


def test_results(client):
    """Minimal test that includes logging in and getting a token"""
    response = client.get("/api/v0/results")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    client.login()
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []


def test_results_methods(client):
    """Ensure that only the GET HTTP method works with /results"""
    client.login()
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []

    response = client.put("/api/v0/results")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.patch("/api/v0/results")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []


def test_get_non_existing_result(client):
    """Ensure that we get a 404 when trying to get a non-existing result"""
    client.login()
    response = client.get("/api/v0/result/benchmark1")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404


def assert_response_data_matches_expected(resp_data: List[Dict], req_data: List[Dict]):
    """
    Check that the response data matches the expected data in a
    backwards-compatible way, i.e. we ignore fields that we didn't
    set but appear in the response.

    Using this function makes it possible to add new fields to the
    schema without breaking the tests.
    """
    # print("xoxoxoxoxoxoxoxox")
    # pprint(resp_data)
    # pprint(req_data)
    assert isinstance(resp_data, list)
    # assert all([isinstance(r, dict) for r in resp_data])
    assert isinstance(req_data, list)
    # assert all([isinstance(r, dict) for r in req_data])
    assert len(resp_data) == len(req_data)
    # assert all(set(req.keys()) in set(resp.keys()) for resp, req in zip(resp_data, req_data))
    for resp, req in zip(resp_data, req_data):
        if isinstance(req, dict):
            for k, v in req.items():
                if k not in resp:
                    pprint(resp)
                    pprint(req)
                    assert False
                if isinstance(v, list):
                    assert_response_data_matches_expected(resp[k], v)
                elif isinstance(v, dict):
                    assert_response_data_matches_expected([resp[k]], [v])
                else:
                    assert resp[k] == v
        elif isinstance(req, list):
            assert_response_data_matches_expected(resp_data, req_data)
        else:
            assert resp == req


def test_add_result(client):
    client.login()

    # Add a result
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" == response.json()[0]["test_name"]

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_add_multiple_test_results_at_once(client):
    """Upload multiple results in one POST request"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    print(vars(response))
    assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" == response.json()[0]["test_name"]

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_add_multiple_tests(client):
    """Add multiple tests and ensure that they are returned"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.post("/api/v0/result/benchmark2", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200

    test_names = [result["test_name"] for result in response.json()]
    for name in ("benchmark1", "benchmark2"):
        assert name in test_names


def test_delete_all_user_results(client):
    """Test that we can delete all a user's results"""
    client.login()

    # Add a result
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" in response.json()[0]["test_name"]

    # Delete all results
    response = client.delete("/api/v0/results")
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_single_result(client):
    """Delete a single test result"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 3.0, "unit": "ms"},
                {"name": "metric2", "value": 4.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]
    test_name = "benchmark1"
    response = client.post(f"/api/v0/result/{test_name}", json=data)
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert test_name in response.json()[0]["test_name"]

    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 200
    assert_response_data_matches_expected(response.json(), data)

    # Delete a single result by timestamp
    response = client.delete(f"/api/v0/result/{test_name}?timestamp=1")
    assert response.status_code == 200

    # Read back the result and check timestamp2 is still there
    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 200
    assert_response_data_matches_expected(response.json(), [data[1], data[2]])

    # Delete the remaining result
    response = client.delete(f"/api/v0/result/{test_name}")
    assert response.status_code == 200

    # Check that the result is gone
    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 404


def test_change_points(client):
    """Run change point detection on a series"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3


def test_register_new_user(unauthenticated_client):
    """Register a new user"""
    data = {
        "email": "foo@bar.com",
        "password": "foobar",
    }
    response = unauthenticated_client.post("/api/v0/auth/register", json=data)
    assert response.status_code == 201
    assert response.json()["is_active"]


def test_unauth_user_get_default_data_test_names(unauthenticated_client):
    """Ensure that unauthenticated users can get the default data"""
    response = unauthenticated_client.get("/api/v0/default/results")
    assert response.status_code == 200
    assert "default_benchmark" in response.json()
    assert len(response.json()) == 1


def test_auth_user_get_default_data_test_names(client):
    """Ensure that authenticated users can get the default data"""
    client.login()
    response = client.get("/api/v0/default/results")
    assert response.status_code == 200
    assert "default_benchmark" in response.json()
    assert len(response.json()) == 1


def test_unauth_get_default_data_test_results(unauthenticated_client):
    """Ensure that users can get the default data"""
    response = unauthenticated_client.get("/api/v0/default/result/default_benchmark")
    assert response.status_code == 200
    from backend.db.db import MockDBStrategy

    assert response.json() == MockDBStrategy.DEFAULT_DATA
    assert len(response.json()) == len(MockDBStrategy.DEFAULT_DATA)


def test_auth_user_get_default_data_test_results(client):
    """Ensure that authenticated users can get the default data"""
    client.login()
    response = client.get("/api/v0/default/result/default_benchmark")
    assert response.status_code == 200
    from backend.db.db import MockDBStrategy

    assert response.json() == MockDBStrategy.DEFAULT_DATA
    assert len(response.json()) == len(MockDBStrategy.DEFAULT_DATA)


def test_disable_change_detection_for_metric(client):
    """Ensure that we can disable change detection for individual metrics"""
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    client.login()
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/changes/disable", json=["metric", "metric2"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert not data["benchmark1"]


def test_disable_and_reenable_changes_for_metrics(client):
    """Ensure that we can disable and then re-enable change detection for metrics"""
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    client.login()
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/changes/disable", json=["metric2"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert not data["benchmark1"]

    # Re-enable change detection for metric2
    response = client.post("/api/v0/result/benchmark1/changes/enable", json=["metric2"])
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3


def test_add_metric_while_disabled(client):
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    client.login()
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert not data["benchmark1"]

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/changes/disable", json=["metric2"]
    )
    assert response.status_code == 200

    # Then add more data, including for metric2
    data = [
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert not data["benchmark1"]

    # Re-enable change detection for metric2
    response = client.post("/api/v0/result/benchmark1/changes/enable", json=["metric2"])
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert data["benchmark1"]
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3


def test_disable_change_for_empty_metrics_fails(client):
    """Ensure that we can't disable change detection for empty metrics"""
    client.login()
    response = client.post("/api/v0/result/benchmark1/changes/disable", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "No metrics to disable change detection for"}


def test_enable_change_for_empty_metrics_succeeds(client):
    """Ensure that we can enable change detection for empty metrics"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/changes/disable", json=["metric2"]
    )
    assert response.status_code == 200

    # Validate that change detection is disabled for metric2
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert not data["benchmark1"]

    # enable change detection for all metrics
    response = client.post("/api/v0/result/benchmark1/changes/enable", json=[])
    assert response.status_code == 200

    # Validate that change detection is enabled for all metrics
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3


def test_changes_data_is_sorted_by_timestamp(client):
    """Ensure that the change points are sorted by timestamp"""
    client.login()

    json = [
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 4,
            "metrics": [
                {"name": "metric1", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=json)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1" in json
    data = json["benchmark1"]
    assert len(data) == 1
    assert data[0]["time"] == 3
    assert len(data[0]["changes"]) == 1
    change = data[0]["changes"][0]
    assert float(change["mean_before"]) == 3.0
    assert float(change["mean_after"]) == 30.0


def test_results_are_sorted_by_timestamp(client):
    """Ensure that the results are sorted by timestamp"""
    client.login()

    data = [
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert len(data) == 3
    for i in range(3):
        assert data[i]["timestamp"] == i + 1


def test_user_adds_result_with_invalid_primary_key(client):
    """Ensure that we can't add a result with an invalid primary key"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "myrepo",
                # Missing branch and git_commit keys
            },
        }
    ]
    response = client.post("/api/v0/result/invalid_test_name", json=data)
    assert response.status_code == 422
    json = response.json()
    print(json)
    assert json["detail"][0]["msg"] == "Field required"
    assert json["detail"][0]["loc"] == ["body", 0, "attributes", "git_commit"]


def test_user_cannot_add_same_result_twice(client):
    """Ensure that we can't add the same result twice"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "myrepo",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 400
    assert response.json()["detail"]["reason"] == "Result already exists for key"
    assert response.json()["detail"]["data"] == {
        "test_name": "benchmark1",
        "timestamp": 1,
        "git_repo": "myrepo",
        "branch": "main",
        "git_commit": "123456",
    }

    # Modify the timestamp and try again and make sure it succeeds
    data[0]["timestamp"] = 2
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Now modify the repo and try again and make sure it succeeds
    data[0]["timestamp"] = 1
    data[0]["attributes"]["git_repo"] = "myrepo2"
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200


def test_duplicate_result_message_includes_key(client):
    """Ensure that the error message for adding a duplicate result includes the key"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "myrepo",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 400
    assert "Result already exists for key" in response.json()["detail"]["reason"]
    dup_key = response.json()["detail"]["data"]
    assert dup_key == {
        "test_name": "benchmark1",
        "timestamp": 1,
        "git_repo": "myrepo",
        "branch": "main",
        "git_commit": "123456",
    }


def test_add_and_get_user_config(client):
    """Ensure that we can store and retrieve user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
            "github_pr": False,
            "github": False,
            "since_days": 14,
        },
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**config, "billing": None, "billing_runners": None}


def test_add_and_get_partial_user_config(client):
    """Ensure that we can store and retrieve user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
            "github_pr": False,
            "github": False,
            "since_days": 14,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {
        **config,
        "billing": None,
        "billing_runners": None,
    }


def test_update_existing_user_config(client):
    """Ensure that we can update an existing user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
            "github_pr": False,
            "github": False,
            "since_days": 14,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {
        **config,
        "billing": None,
        "billing_runners": None,
    }

    new_config = {
        "notifiers": {
            "slack": False,
            "github_pr": False,
            "github": True,
            "since_days": 14,
        }
    }
    response = client.put("/api/v0/user/config", json=new_config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {
        **new_config,
        "billing": None,
        "billing_runners": None,
    }


def test_create_test_result_with_slash_separator(client):
    """Ensure that we can create a test result with a slash separator"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_create_test_result_with_slash_separator_and_get_all_results(client):
    """Ensure that we can create a test result with a slash separator and get all results"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json[0]["test_name"] == "benchmark1/test"


def test_calculate_changes_for_test_with_slashes(client):
    """Ensure that we can calculate changes for a test with slashes"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    for ch in json["benchmark1/test"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert json["benchmark1/test"][0]["time"] == 3


def test_disable_changes_for_test_with_slashes(client):
    """Make sure we can disable changes for a test with slashes"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    for ch in json["benchmark1/test"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert json["benchmark1/test"][0]["time"] == 3

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/test/changes/disable", json=["metric2"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    assert not json["benchmark1/test"]


def test_disable_reenable_changes_for_test_with_slashes(client):
    """Make sure we can disable and re-enable changes for a test with slashes"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    for ch in json["benchmark1/test"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert json["benchmark1/test"][0]["time"] == 3

    # Disable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/test/changes/disable", json=["metric2"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    assert not json["benchmark1/test"]

    # Re-enable change detection for metric2
    response = client.post(
        "/api/v0/result/benchmark1/test/changes/enable", json=["metric2"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "benchmark1/test" in json
    for ch in json["benchmark1/test"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert json["benchmark1/test"][0]["time"] == 3


def test_delete_test_name_with_slashes(client):
    """Ensure that we can delete a test name with slashes"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1/test", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/test")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)

    response = client.delete("/api/v0/result/benchmark1/test")
    assert response.status_code == 200


def test_setting_min_magnitude_config_shows_no_change_points(client):
    """Ensure that setting min_magnitude to a high value shows no change points"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"

    config = {
        "core": {
            "max_pvalue": 0.01,
            "min_magnitude": 20.0,
        }
    }

    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    assert not data["benchmark1"]


def test_superuser_can_see_all_test_results(client):
    """Ensure that superusers can see all test results"""
    superuser_client = SuperuserClient(app)
    superuser_client.login()

    # Add some results for regular user
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Ensure superuser can use admin API to view all results
    response = superuser_client.get("/api/v0/admin/results")
    assert response.status_code == 200
    superuser_data = response.json()
    assert len(superuser_data) == 4

    client_results = superuser_data[client.email]
    assert client_results == [{"test_name": "benchmark1"}]


def test_regular_user_cannot_access_admin_api(client):
    """Ensure that regular users cannot access the admin API"""
    client.login()
    response = client.get("/api/v0/admin/results")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_get_results_for_users_test(client):
    """Ensure that we can get results for a user's test"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    superuser_client = SuperuserClient(app)
    superuser_client.login()

    response = superuser_client.get("/api/v0/admin/results")
    assert response.status_code == 200

    superuser_data = response.json()
    assert len(superuser_data) == 4

    client_results = superuser_data[client.email]
    assert client_results == [{"test_name": "benchmark1"}]

    response = superuser_client.get(f"/api/v0/admin/result/{client.email}/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["timestamp"] == 1
    assert_response_data_matches_expected(response.json(), data)


def test_admin_api_get_results_with_invalid_email():
    """Ensure that the admin API returns 400 for invalid email"""
    superuser_client = SuperuserClient(app)
    superuser_client.login()

    invalid_email_addresses = [
        "invalidemail",
        "invalidemail@",
        "invalidemail@.com",
        "",
        "@",
    ]
    for invalid_email in invalid_email_addresses:
        response = superuser_client.get(f"/api/v0/admin/result/{invalid_email}")
        assert response.status_code == 404
        assert response.json() == {"detail": "No such user exists"}


def test_attributes_without_list(client):
    """Ensure attribute values can be singular and not part of a list"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_mark_results_as_public(client):
    """Ensure that we can mark results as public"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    data = response.json()
    assert not data

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]
    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["public"] is True


def test_results_have_no_config_by_default(client):
    """Ensure that results have no config by default (and are private)"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert not response.json()


def test_mark_results_as_private(client):
    """Ensure that we can mark results as private"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert not response.json()

    config = [
        {
            "public": False,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]
    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["public"] is False


def test_set_test_config_different_repos(client):
    """Ensure that we can set test config for different repos"""
    client.login()

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        },
        {
            "public": False,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio2",
                "branch": "main",
            },
        },
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json() == config


def test_set_test_config_same_repo_different_branch(client):
    """Ensure that we can set test config for the same repo but different branches"""
    client.login()

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        },
        {
            "public": False,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "feature",
            },
        },
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json() == config


def test_config_requires_attributes_with_git_repo_and_branch(client):
    """Ensure that test config requires attributes with git_repo and branch"""
    client.login()

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/notnyrkio/nyrkio",
                "branch": "main",
            },
        },
        {
            "public": False,
            "attributes": {
                "git_repo": "https://github.com/notnyrkio/nyrkio",
            },
        },
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_delete_test_config(client):
    """Ensure that we can delete a test config"""
    client.login()

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json() == config

    response = client.delete("/api/v0/config/benchmark1")
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json() == []


def test_public_test_results(client, unauthenticated_client):
    """Ensure that we can fetch public test results"""
    response = unauthenticated_client.get("/api/v0/public/results")
    assert response.status_code == 200
    assert response.json() == []

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    client.login()
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = unauthenticated_client.get("/api/v0/public/results")
    assert response.status_code == 200
    assert response.json() == [
        {
            "test_name": "nyrkio/nyrkio/main/benchmark1",
        }
    ]

    response = unauthenticated_client.get(
        "/api/v0/public/result/nyrkio/nyrkio/main/benchmark1"
    )
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_invalid_public_test_name(unauthenticated_client):
    """Ensure that we can't fetch invalid public test results"""
    invalid_urls = (
        "/api/v0/public/result",
        "/api/v0/public/result/foo",
        "/api/v0/public/result/foo/bar",
        "/api/v0/public/result/foo/bar/baz",
    )

    for url in invalid_urls:
        response = unauthenticated_client.get(url)
        assert response.status_code == 404
        assert response.json() == {"detail": "No such test exists"}


def test_only_one_user_can_make_a_test_public(client):
    """Ensure that only one user can make a test public"""
    client1 = client
    client1.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    response = client1.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = client1.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    from backend.auth import auth

    asyncio.run(auth.add_user("user2@foo.com", "foo"))
    client2 = AuthenticatedTestClient(app)
    client2.email = "user2@foo.com"
    client2.login()

    response = client2.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client2.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 409


def test_delete_test_config_deletes_public_test(client):
    """Ensure that we can delete a public test config"""
    client.login()

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200

    response = client.delete("/api/v0/config/benchmark1")
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json() == []


def test_same_test_name_different_repos(client):
    """Ensure that we can have the same test name for different repos"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio2",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200

    assert len(response.json()) == 1
    assert response.json()[0]["test_name"] == "benchmark1"

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200

    assert len(response.json()) == 2

    repos = []
    for result in response.json():
        repos.append(result["attributes"]["git_repo"])

    assert repos == [
        "https://github.com/nyrkio/nyrkio",
        "https://github.com/nyrkio/nyrkio2",
    ]

    # Make benchmark1 public for github.com/nyrkio/nyrkio
    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio2",
                "branch": "main",
            },
        }
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["public"] is True

    unauth_client = TestClient(app)
    response = unauth_client.get("/api/v0/public/results")
    assert response.status_code == 200
    assert response.json() == [
        {
            "test_name": "nyrkio/nyrkio2/main/benchmark1",
        }
    ]

    response = unauth_client.get("/api/v0/public/result/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 404

    response = unauth_client.get("/api/v0/public/result/nyrkio/nyrkio2/main/benchmark1")
    assert response.status_code == 200


def test_extra_info(client):
    """Ensure that we can store and retrieve extra info"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)

    # Upload some arbitrarily nested extra info
    nested_data = dict(data[0])
    nested_data["timestamp"] = 2
    nested_data["extra_info"] = {"foo": {"bar": {"baz": 1}, "qux": [1, 2, 3]}}
    response = client.post("/api/v0/result/benchmark1", json=[nested_data])
    assert response.status_code == 200

    data.append(nested_data)

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_public_result_exists(client):
    """Fail gracefully if a public result exists and we add a second"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = client.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/config/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["public"] is True

    from backend.auth import auth

    asyncio.run(auth.add_user("user2@foo.com", "foo"))
    client2 = AuthenticatedTestClient(app)
    client2.email = "user2@foo.com"
    client2.login()

    response = client2.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client2.post("/api/v0/config/benchmark1", json=config)
    assert response.status_code == 409

    # If the above HTTP POST failed we should not see the result in the public results
    response = client.get("/api/v0/public/results")
    assert response.status_code == 200
    assert response.json() == [
        {
            "test_name": "nyrkio/nyrkio/main/benchmark1",
        }
    ]


def test_extract_public_test_name():
    config = {
        "attributes": {"git_repo": "https://github.com/nyrkio/nyrkio", "branch": "main"}
    }

    name = extract_public_test_name(config["attributes"])
    assert name == "nyrkio/nyrkio/main"


def test_auth_user_generate_token(client):
    """Ensure that a user can generate a new token"""
    client.login()

    response = client.post("/api/v0/auth/token")
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"


def test_calc_changes_after_update(client):
    """Ensure that we can calculate changes after updating a test"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 1
    assert json["benchmark1"][0]["time"] == 3

    # Hit the cache
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 1
    assert json["benchmark1"][0]["time"] == 3

    # Update final result
    data[-1]["metrics"][0]["value"] = 1.0
    response = client.put("/api/v0/result/benchmark1", json=[data[-1]])
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 0


def test_disable_metric_invalidates_change_points(client):
    """Ensure that disabling a metric invalidates change points"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 30.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 1
    assert json["benchmark1"][0]["time"] == 3
    assert len(json["benchmark1"][0]["changes"]) == 2
    assert json["benchmark1"][0]["changes"][0]["metric"] == "metric1"
    assert json["benchmark1"][0]["changes"][1]["metric"] == "metric2"

    # Disable metric1
    response = client.post(
        "/api/v0/result/benchmark1/changes/disable", json=["metric1"]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 1
    assert json["benchmark1"][0]["time"] == 3
    assert len(json["benchmark1"][0]["changes"]) == 1
    assert json["benchmark1"][0]["changes"][0]["metric"] == "metric2"


def test_default_data_changes(unauthenticated_client):
    """Ensure that we can get change points for default data"""
    client = unauthenticated_client

    response = client.get("/api/v0/default/result/default_benchmark/changes")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "default_benchmark" in json
    assert len(json["default_benchmark"]) == 1
    assert (
        json["default_benchmark"][0]["time"]
        == MockDBStrategy.DEFAULT_DATA[-1]["timestamp"]
    )


def test_put_existing_result(client):
    """Ensure that we can update an existing result"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    data[0]["metrics"][0]["value"] = 2.0
    response = client.put("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


def test_build_series():
    """
    Ensure that we can build a series with and without metadata
    """
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "6789a",
            },
        },
    ]

    series = _build_result_series("test_name", data, [{}, {}])
    assert series.last_modified() == NULL_DATETIME

    now = datetime.now()
    series = _build_result_series(
        "test_name", data, [{"last_modified": now}, {"last_modified": now}]
    )
    assert series.last_modified() == now


def test_build_series_with_partial_metadata():
    """
    Ensure that we can build a series with partial metadata

    Users might have a mixture of test results, some with metadata and some
    without.
    """
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "6789a",
            },
        },
    ]

    now = datetime.now()

    # Empty metadata for last result
    series = _build_result_series("test_name", data, [{"last_modified": now}, {}])
    assert series.last_modified() == now

    # Empty metadata for first result
    series = _build_result_series("test_name", data, [{}, {"last_modified": now}])
    assert series.last_modified() == now


def test_results_returns_sorted_test_names(client):
    """Ensure that the results endpoint returns sorted test names"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]

    for b in ("benchmark3", "benchmark2", "benchmark1"):
        response = client.post(f"/api/v0/result/{b}", json=data)
        assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200
    json = response.json()
    assert json == [
        {"test_name": "benchmark1"},
        {"test_name": "benchmark2"},
        {"test_name": "benchmark3"},
    ]


def test_payload_missing_metric_unit_doesnt_persist(client):
    """Ensure that a payload missing metric unit doesn't persist"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code >= 400

    # Check to see if the result was persisted
    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 404
