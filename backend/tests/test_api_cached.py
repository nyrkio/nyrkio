from typing import Dict, List


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

    response2 = client.get("/api/v0/result/benchmark1")
    assert response2.json() == {"detail": "Not Found"}
    assert response2.status_code == 404


def assert_response_data_matches_expected(resp_data: List[Dict], req_data: List[Dict]):
    """
    Check that the response data matches the expected data in a
    backwards-compatible way, i.e. we ignore fields that we didn't
    set but appear in the response.

    Using this function makes it possible to add new fields to the
    schema without breaking the tests.
    """
    assert len(resp_data) == len(req_data)
    assert any(resp.items() >= req.items() for resp, req in zip(resp_data, req_data))


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

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)
    response = client.get("/api/v0/result/benchmark2")
    assert response.status_code == 200
    json = response.json()
    assert_response_data_matches_expected(json, data)


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

    # Read the same again (cached)
    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 200
    assert_response_data_matches_expected(response.json(), [data[1], data[2]])

    # Delete the remaining result
    response = client.delete(f"/api/v0/result/{test_name}")
    assert response.status_code == 200

    # Check that the result is gone
    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 404
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


def test_incremental_change_points(client):
    """Run change point detection on a series,  then add a point"""
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

    new_data = [
        {
            "timestamp": 4,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 31.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123457",
            },
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=new_data)
    assert response.status_code == 200
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 3


def test_incremental_change_points_not_monotonic(client):
    """incremental fails because added point has a lower timestamp"""
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
            "timestamp": 6,
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
            "timestamp": 7,
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
    assert data["benchmark1"][0]["time"] == 7

    new_data = [
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123457",
            },
        }
    ]
    # This will use full algorithm. Looks the same to the user
    response = client.post("/api/v0/result/benchmark1", json=new_data)
    assert response.status_code == 200
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "benchmark1" in data
    for ch in data["benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"
    assert data["benchmark1"][0]["time"] == 7


def test_unauth_get_default_data_test_results(unauthenticated_client):
    """Ensure that users can get the default data"""
    response = unauthenticated_client.get("/api/v0/default/result/default_benchmark")
    assert response.status_code == 200
    from backend.db.db import MockDBStrategy

    assert response.json() == MockDBStrategy.DEFAULT_DATA
    assert len(response.json()) == len(MockDBStrategy.DEFAULT_DATA)

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

    assert response.status_code == 200
    from backend.db.db import MockDBStrategy

    assert response.json() == MockDBStrategy.DEFAULT_DATA
    assert len(response.json()) == len(MockDBStrategy.DEFAULT_DATA)


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
