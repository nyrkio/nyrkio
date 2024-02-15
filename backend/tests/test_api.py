from backend.api.api import app
from conftest import SuperuserClient


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


def test_add_result(client):
    client.login()

    # Add a result
    data = [
        {
            "timestamp": 1,
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
    assert len(json) == 1
    assert json[0] == data[0]


def test_add_multiple_test_results_at_once(client):
    """Upload multiple results in one POST request"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
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
    assert len(json) == 2
    assert data[0] in json
    assert data[1] in json


def test_add_multiple_tests(client):
    """Add multiple tests and ensure that they are returned"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
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
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 3,
            "metrics": [{"metric1": 3.0, "metric2": 4.0}],
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
    assert response.json() == data

    # Delete a single result by timestamp
    response = client.delete(f"/api/v0/result/{test_name}?timestamp=1")
    assert response.status_code == 200

    # Read back the result and check timestamp2 is still there
    response = client.get(f"/api/v0/result/{test_name}")
    assert response.status_code == 200
    assert response.json() == [data[1], data[2]]

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

    assert response.json() == [MockDBStrategy.DEFAULT_DATA]
    assert len(response.json()) == 1


def test_auth_user_get_default_data_test_results(client):
    """Ensure that authenticated users can get the default data"""
    client.login()
    response = client.get("/api/v0/default/result/default_benchmark")
    assert response.status_code == 200
    from backend.db.db import MockDBStrategy

    assert response.json() == [MockDBStrategy.DEFAULT_DATA]
    assert len(response.json()) == 1


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
    assert response.status_code == 400
    assert response.json()["detail"]["reason"] == "Result is missing required keys"
    assert response.json()["detail"]["data"] == [
        "attributes.branch",
        "attributes.git_commit",
    ]


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
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**config, "core": None}


def test_update_existing_user_config(client):
    """Ensure that we can update an existing user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**config, "core": None}

    new_config = {"notifiers": {"slack": False}}
    response = client.put("/api/v0/user/config", json=new_config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**new_config, "core": None}


def test_create_test_result_with_slash_separator(client):
    """Ensure that we can create a test result with a slash separator"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
    assert len(json) == 1
    assert json[0] == data[0]


def test_create_test_result_with_slash_separator_and_get_all_results(client):
    """Ensure that we can create a test result with a slash separator and get all results"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
    assert len(json) == 1
    assert json[0] == data[0]

    response = client.delete("/api/v0/result/benchmark1/test")
    assert response.status_code == 200


def test_user_config_set_min_magnitude_max_pvalue(client):
    """Ensure that we can set min_magnitude and max_pvalue in user config"""
    client.login()
    config = {
        "core": {
            "min_magnitude": 0.5,
            "max_pvalue": 0.01,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200

    assert response.json() == {**config, "notifiers": None}


def test_user_config_set_max_pvalue_invalid(client):
    """Ensure that we can't set invalid max_pvalue in user config"""
    client.login()
    config = {
        "core": {
            "min_magnitude": 0.5,
            "max_pvalue": 1.01,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 400
    assert response.json() == {"detail": "max_pvalue must be less than or equal to 1.0"}


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
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
    assert len(superuser_data) == 2

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
            "metrics": [{"metric1": 1.0, "metric2": 2.0}],
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
    assert len(superuser_data) == 2

    client_results = superuser_data[client.email]
    assert client_results == [{"test_name": "benchmark1"}]

    response = superuser_client.get(f"/api/v0/admin/result/{client.email}/benchmark1")
    assert response.status_code == 200
    assert response.json()[0]["timestamp"] == 1
    assert response.json() == data


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
    assert len(json) == 1
    assert json[0] == data[0]
