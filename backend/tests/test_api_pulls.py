import pytest


def test_pr_add_result(client):
    """Ensure that we can add a PR result"""
    client.login()

    pull_number = 123
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
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
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
        }
    ]


@pytest.mark.skip(
    "benchmark_names doubles on the second time. This is essentially just testing MockDBStrategy so no point in debugging too much."
)
def test_pr_put_result(client):
    """Ensure that we can add a PR result twice with PUT, yielding only one result"""
    client.login()

    pull_number = 123
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12345",
        },
        "extra_info": {},
    }

    benchmark_names = ["benchmark1", "benchmark2"]
    for benchmark_name in benchmark_names:
        response = client.put(
            f"/api/v0/pulls/{repo}/{pull_number}/result/{benchmark_name}", json=[data]
        )
        assert response.status_code == 200

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    print(json)
    assert len(json) == 1

    assert json == [
        {
            "pull_number": pull_number,
            "test_names": benchmark_names,
            "git_commit": "12345",
            "git_repo": repo,
        }
    ]

    for benchmark_name in benchmark_names:
        response = client.put(
            f"/api/v0/pulls/{repo}/{pull_number}/result/{benchmark_name}", json=[data]
        )
        assert response.status_code == 200

    response = client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    print(json)
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
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
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
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
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
                "git_commit": "12345a",
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
                "git_commit": "12345b",
            },
            "extra_info": {},
        },
    ]

    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    pull_number = 123
    git_commit = "12345c"
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
                "git_repo": "https://github.com/" + repo,
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
    print(json)
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
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
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
    print(json)
    assert len(json) == 1
    assert json == [
        {
            "pull_number": pull_number,
            "test_names": [test_name],
            "git_commit": git_commit,
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
        }
    ]


def test_pr_get_individual_result(client):
    """Ensure that we can get individual PR results"""
    client.login()

    pull_number = 123
    git_commit = "12345"
    test_name = "benchmark1"
    repo = "nyrkio/nyrkio"
    data = {
        "timestamp": 1,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": git_commit,
        },
    }

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/{test_name}", json=[data]
    )
    assert response.status_code == 200

    response = client.get(f"/api/v0/pulls/{repo}/{pull_number}/result/{test_name}")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json[0]["timestamp"] == 1


def test_only_last_pr_result_used_in_changes(client):
    """Ensure that only the last PR result is used in changes"""
    client.login()

    test_name = "benchmark1"
    repo = "nyrkio/nyrkio"

    # Add a bunch of regular test results that set the baseline for a metric
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "12345",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "12345",
            },
        },
    ]

    response = client.post(f"/api/v0/result/{test_name}", json=data)
    assert response.status_code == 200

    response = client.get(f"/api/v0/result/{test_name}/changes")
    assert response.status_code == 200
    json = response.json()
    assert "benchmark1" in json
    assert len(json["benchmark1"]) == 0

    pull_number = 123
    git_commit = "abcdef"
    data = {
        "timestamp": 10,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 20.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": git_commit,
        },
    }

    response = client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/{test_name}", json=[data]
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v0/pulls/{repo}/{pull_number}/changes/{git_commit}/test/{test_name}"
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json[0]["benchmark1"][0]["time"] == 10

    # Ensure that we get the correct number of change points when we add more
    # PR results.
    num_results = 5
    last_commit = f"{git_commit}{num_results - 1}"
    for i in range(1, num_results):
        data["timestamp"] = 10 + i
        data["metrics"][1]["value"] = 200.0
        data["attributes"]["git_commit"] = f"{git_commit}{i}"
        response = client.post(
            f"/api/v0/pulls/{repo}/{pull_number}/result/{test_name}", json=[data]
        )
        assert response.status_code == 200

    response = client.get(
        f"/api/v0/pulls/{repo}/{pull_number}/changes/{git_commit}/test/{test_name}"
    )
    assert response.status_code == 200

    json = response.json()
    assert len(json) == 1
    assert len(json[0]["benchmark1"]) == 1
    assert json[0]["benchmark1"][0]["time"] == 10

    response = client.get(
        f"/api/v0/pulls/{repo}/{pull_number}/changes/{last_commit}/test/{test_name}"
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert len(json[0]["benchmark1"]) == 1
    assert json[0]["benchmark1"][0]["time"] == 10 + num_results - 1


def test_pr_many_tests(client):
    """Ensure that we can add a PR result"""
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
                "git_commit": "123",
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
                "git_commit": "1234",
            },
            "extra_info": {},
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
                "git_commit": "12345",
            },
            "extra_info": {},
        },
    ]

    benchmark_names = [
        "benchmark1",
        "benchmark2",
        "benchmark3",
        "benchmark4",
        "benchmark5",
    ]
    for benchmark_name in benchmark_names:
        response = client.post("/api/v0/result/" + benchmark_name, json=data)

    pull_number = 66666
    repo = "nyrkio/nyrkio"

    prdata = {
        "timestamp": 10,
        "metrics": [
            {"name": "metric1", "value": 22.0, "unit": "ms"},
            {"name": "metric2", "value": 30.0, "unit": "ms"},
            {"name": "metric3", "value": 300.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "main",
            "git_commit": "123456",
        },
        "extra_info": {},
    }
    benchmark_names = [
        "benchmark1",
        "benchmark2",
        "benchmark3",
        "benchmark4",
        "benchmark5",
    ]
    for benchmark_name in benchmark_names:
        response = client.post(
            f"/api/v0/pulls/{repo}/{pull_number}/result/{benchmark_name}", json=[prdata]
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
            "git_commit": "123456",
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
        }
    ]

    response = client.get(
        f"/api/v0/pulls/{repo}/{pull_number}/changes/123456?notify=1",
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 5
    for obj in json:
        for k, v in obj.items():
            assert len(v) == 1
