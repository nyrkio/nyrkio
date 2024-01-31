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
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": [{"metric1": 2.0, "metric2": 3.0}],
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 3,
            "metrics": [{"metric1": 3.0, "metric2": 4.0}],
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {"attr1": "value1", "attr2": "value2"},
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
