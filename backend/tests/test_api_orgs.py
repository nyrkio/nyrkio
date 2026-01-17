import pytest

from backend.api.api import app

from backend.conftest import GitHubClient


def test_org_results(client):
    """Ensure that we can fetch results for a user's organization"""
    client.login()

    response = client.get("/api/v0/orgs")
    assert response.status_code == 200
    assert response.json() == []

    gh_client = GitHubClient(app)
    gh_client.login()
    response = gh_client.get("/api/v0/orgs")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 2

    org_name = json[0]["login"]
    repo = "nyrkio"

    response = gh_client.get("/api/v0/orgs/results")
    assert response.status_code == 200
    json = response.json()
    assert json == []

    data = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [{"name": "metric1", "value": 2.0, "unit": "ms"}],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
    ]

    response = gh_client.post(
        f"/api/v0/orgs/result/{org_name}/{repo}/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/results")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json == [{"test_name": f"{org_name}/{repo}/main/benchmark1"}]

    response = gh_client.delete(
        f"/api/v0/orgs/result/{org_name}/{repo}/main/benchmark1"
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/results")
    assert response.status_code == 200
    json = response.json()
    assert json == []


def test_invalid_org(gh_client):
    """Ensure that we get a 404 for an invalid org"""
    gh_client.login()

    response = gh_client.get("/api/v0/orgs/result/invalid/nyrkio/main/benchmark1")
    assert response.status_code == 404
    assert response.json() == {"detail": "No such organization exists"}

    response = gh_client.delete("/api/v0/orgs/result/invalid/nyrkio/main/benchmark1")
    assert response.status_code == 404
    assert response.json() == {"detail": "No such organization exists"}


def test_add_result_for_invalid_org(gh_client):
    """Ensure that users cannot add results for an org they're not a member of"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio3/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 404


def test_fetch_org_results(gh_client):
    """Ensure that we can fetch org results"""
    gh_client.login()

    response = gh_client.get("/api/v0/orgs/results")
    assert response.status_code == 200
    assert response.json() == []

    org_name = "nyrkio"
    repo = "nyrkio"

    data = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = gh_client.post(
        f"/api/v0/orgs/result/{org_name}/{repo}/main/benchmark1", json=data
    )

    response = gh_client.get(f"/api/v0/orgs/result/{org_name}/{repo}/main/benchmark1")
    assert response.status_code == 200


def test_delete_org_result_by_timestamp(gh_client):
    """Ensure that we can delete an org result by timestamp"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [{"name": "metric1", "value": 2.0, "unit": "ms"}],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 2

    response = gh_client.delete(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1?timestamp=1"
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1


def test_org_result_changes(gh_client):
    """Ensure that we can fetch org result changes"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1/changes"
    )
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "nyrkio/nyrkio/main/benchmark1" in json
    for ch in json["nyrkio/nyrkio/main/benchmark1"][0]["changes"]:
        assert ch["metric"] == "metric2"

    assert json["nyrkio/nyrkio/main/benchmark1"][0]["time"] == 3


def test_org_test_config_public(gh_client):
    """Ensure that we make an organization test public"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 1.0, "unit": "ms"}],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        }
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    data = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = gh_client.post(
        "/api/v0/orgs/config/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/config/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert json
    assert json == data

    response = gh_client.get("/api/v0/public/results")
    assert response.status_code == 200
    json = response.json()
    assert json == [
        {
            "test_name": "nyrkio/nyrkio/main/benchmark1",
        }
    ]

    response = gh_client.get("/api/v0/public/result/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200

    # Delete the test config
    response = gh_client.delete("/api/v0/orgs/config/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/config/nyrkio/nyrkio/main/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert json == []

    response = gh_client.get("/api/v0/public/results")
    assert response.status_code == 200
    assert response.json() == []


def test_org_public_test_changes(gh_client):
    """Ensure that we can fetch public org result changes"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "abc123",
            },
        },
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    data = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    response = gh_client.post(
        "/api/v0/orgs/config/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get(
        "/api/v0/public/result/nyrkio/nyrkio/main/benchmark1/changes"
    )
    assert response.status_code == 200
    json = response.json()
    assert json
    assert "nyrkio/nyrkio/main/benchmark1" in json
    assert len(json["nyrkio/nyrkio/main/benchmark1"]) == 1
    assert json["nyrkio/nyrkio/main/benchmark1"][0]["time"] == 3


def test_org_config(gh_client):
    """Ensure that we can set and get an organization config"""
    gh_client.login()

    data = {
        "core": {
            "min_magnitude": 1.0,
            "max_pvalue": 0.05,
        },
        "notifiers": None,
        "billing": None,
    }

    response = gh_client.post("/api/v0/orgs/org/nyrkio", json=data)
    assert response.status_code == 200

    response = gh_client.get("/api/v0/orgs/org/nyrkio")
    assert response.status_code == 200
    json = response.json()
    assert json == {
        "core": {
            "min_magnitude": 1.0,
            "max_pvalue": 0.05,
        }
    }


@pytest.mark.skip("Pydantic model isn't validating correctly")
def test_org_with_invalid_config_items(gh_client):
    """Ensure that we get a 400 for an invalid org config"""
    gh_client.login()

    data = {
        "core": {
            "min_magnitude": 1.0,
            "max_pvalue": 1.05,
        },
        "notifiers": None,
    }

    response = gh_client.post("/api/v0/orgs/org/nyrkio", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "max_pvalue must be less than or equal to 1.0"}

    data["core"]["max_pvalue"] = 1.0
    data["core"]["this_is_invalid"] = 1.0
    response = gh_client.post("/api/v0/orgs/org/nyrkio", json=data)
    assert response.status_code == 400


def test_org_config_min_magnitude(gh_client):
    """Ensure that we can set the min_magnitude for organization config"""
    gh_client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "bar"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 3.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "4567889",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
            ],
            "extra_info": {"foo": "baz"},
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "abc123",
            },
        },
    ]

    response = gh_client.post(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1", json=data
    )
    assert response.status_code == 200

    response = gh_client.get(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1/changes"
    )
    assert response.status_code == 200
    print(response)
    json = response.json()
    assert json
    assert "nyrkio/nyrkio/main/benchmark1" in json
    assert len(json["nyrkio/nyrkio/main/benchmark1"]) == 1
    assert json["nyrkio/nyrkio/main/benchmark1"][0]["time"] == 3

    data = {
        "core": {
            "min_magnitude": 500.0,
            "max_pvalue": 0.05,
        },
        "notifiers": None,
    }

    response = gh_client.post("/api/v0/orgs/org/nyrkio", json=data)
    assert response.status_code == 200

    response = gh_client.get(
        "/api/v0/orgs/result/nyrkio/nyrkio/main/benchmark1/changes"
    )
    assert response.status_code == 200

    json = response.json()
    assert json
    assert len(json["nyrkio/nyrkio/main/benchmark1"]) == 0
