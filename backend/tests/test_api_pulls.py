def test_pr_add_result(client):
    """Ensure that we can add a PR result"""
    client.login()

    pull_number = 123
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [{"metric1": 1.0, "metric2": 2.0}],
        "attributes": {
            "git_repo": repo,
            "branch": "main",
            "git_commit": "12345",
        },
        "extra_info": {},
    }

    benchmark_names = ["benchmark1", "benchmark2"]
    for benchmark_name in benchmark_names:
        response = client.post(
            f"/api/v0/pulls/{repo}/{pull_number}/result/{benchmark_name}", json=[data]
        )
        assert response.status_code == 200

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    assert json == [
        {
            "pull_number": pull_number,
            "test_names": benchmark_names,
            "git_commit": "12345",
            "git_repo": repo,
        }
    ]


def test_pr_pulls_doesnt_show_regular_results(client):
    """Ensure that /api/v0/pulls doesn't show regular results"""
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
                "git_commit": "12345",
            },
            "extra_info": {},
        }
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert not json


def test_pr_delete_result(client):
    """Ensure that we can delete a PR result"""
    client.login()

    pull_number = 123
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [{"metric1": 1.0, "metric2": 2.0}],
        "attributes": {
            "git_repo": repo,
            "branch": "main",
            "git_commit": "12345",
        },
        "extra_info": {},
    }

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = client.delete(f"/api/v0/pulls/{repo}/{pull_number}")
    assert response.status_code == 200

    response = client.get(f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1")
    assert response.status_code == 404

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert not json

    # Adding new pull request results shouldn't ressurect the old one
    data["timestamp"] = 2
    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = client.get(f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1")
    assert response.status_code == 200

    json = response.json()
    assert len(json) == 1


def test_pr_add_fails_with_identical_timestamp(client):
    """Ensure that adding a PR result with an identical timestamp fails"""
    client.login()

    pull_number = 123
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [{"metric1": 1.0, "metric2": 2.0}],
        "attributes": {
            "git_repo": repo,
            "branch": "main",
            "git_commit": "12345",
        },
        "extra_info": {},
    }

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 400


def test_pr_add_results_with_non_pr_results(client):
    """Ensure that we can add results at /api/v0/result/ and a pr result"""
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
            "extra_info": {},
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "12345",
            },
            "extra_info": {},
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    pull_number = 123
    git_commit = "12345"
    repo = "nyrkio/nyrkio"
    pr_data = [
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 20.0, "unit": "ms"},
                {"name": "metric2", "value": 30.0, "unit": "ms"},
                {"name": "metric3", "value": 30.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": repo,
                "branch": "main",
                "git_commit": git_commit,
            },
            "extra_info": {},
        }
    ]

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=pr_data
    )
    assert response.status_code == 200

    # Check that we don't see the PR result in the regular results
    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 2
    assert json[0]["timestamp"] == 1
    assert json[1]["timestamp"] == 2

    # Check we detect the performance change from the PR result, but not the regular results
    response = client.get("/api/v0/result/benchmark1/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 0

    response = client.get(f"/api/v0/pulls/{repo}/{pull_number}/changes/{git_commit}")
    assert response.status_code == 200
    json = response.json()
    assert list(filter(lambda x: "benchmark1" in x.keys(), json))
    assert len(json) == 1
    result = json[0]
    assert result["benchmark1"][0]["time"] == 3


def test_pulls_changes_on_non_existent_pr(client):
    """Ensure that we get a 404 for changes on a non-existent PR"""
    client.login()

    response = client.get("/api/v0/pulls/org/repo/123/changes/1234")
    assert response.status_code == 404


def test_pr_pulls(client):
    """Ensure that we can get PRs"""
    client.login()

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    assert response.json() == []

    pull_number = 123
    git_commit = "12345"
    test_name = "benchmark1"
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [{"metric1": 1.0, "metric2": 2.0}],
        "attributes": {
            "git_repo": repo,
            "branch": "main",
            "git_commit": git_commit,
        },
    }

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/{test_name}", json=[data]
    )
    assert response.status_code == 200

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json == [
        {
            "pull_number": pull_number,
            "test_names": [test_name],
            "git_commit": git_commit,
            "git_repo": repo,
        }
    ]
