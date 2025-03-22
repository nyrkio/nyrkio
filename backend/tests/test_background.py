from backend.api.api import app

from backend.tests.test_api import assert_response_data_matches_expected
from conftest import SuperuserClient


def test_summary(client):
    """Upload multiple results, that include a change, then verify summary end point"""
    superuser_client = SuperuserClient(app)
    superuser_client.login()
    # client.login()
    client = superuser_client

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
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
                {"name": "metric1", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 5,
            "metrics": [
                {"name": "metric1", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
    ]
    response = client.post("/api/v0/result/a/b/c/d/e/f", json=data)
    print(vars(response))
    assert response.status_code == 200

    response = client.get("/api/v0/result/a/b/c/d/e/f/changes")
    assert response.status_code == 200
    json = response.json()
    print("changes: {}: {}".format(type(json), json))
    expected = {
        "a/b/c/d/e/f": [
            {
                "time": 3,
                "attributes": {
                    "git_commit": "123456",
                    "branch": "main",
                    "git_repo": "https://github.com/nyrkio/nyrkio",
                },
                "changes": [
                    {
                        "metric": "metric1",
                        "index": 2,
                        "time": 3,
                        "forward_change_percent": "100",
                        "magnitude": "1.000000",
                        "mean_before": "1.000000",
                        "stddev_before": "0.000000",
                        "mean_after": "2.000000",
                        "stddev_after": "0.000000",
                        "pvalue": "0.000000",
                    }
                ],
            }
        ]
    }

    assert_response_data_matches_expected([json], [expected])

    # superuser_client = SuperuserClient(app)
    # superuser_client.login()
    response = superuser_client.get("/api/v0/results/precompute")
    print(vars(response))
    assert response.status_code == 200

    # response = client.get("/api/v0/result/a/b/c/d/e/f/summary")
    # assert response.status_code == 200
    # json = response.json()
    # expected = [{}]
    # assert_response_data_matches_expected(json, expected)

    response = client.get("/api/v0/result/a/b/c/d/e/f/changes")
    assert response.status_code == 200
    json = response.json()
    print("changes: {}: {}".format(type(json), json))

    response = client.get("/api/v0/result/a/b/c/d/e/summary")
    print(response.json())
    assert response.status_code == 200
    json = response.json()
    expected = {
        "total_change_points": 1,
        "newest_time": 3,
        "newest_test_name": "a/b/c/d/e/f",
        "oldest_time": 3,
        "oldest_test_name": "a/b/c/d/e/f",
        "newest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "oldest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "largest_change": 100.0,
        "largest_test_name": "a/b/c/d/e/f",
        "largest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
    }
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/d/summary")
    print(response.json())
    assert response.status_code == 200
    json = response.json()
    expected = {
        "total_change_points": 1,
        "newest_time": 3,
        "newest_test_name": "a/b/c/d/e/f",
        "oldest_time": 3,
        "oldest_test_name": "a/b/c/d/e/f",
        "newest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "oldest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "largest_change": 100.0,
        "largest_test_name": "a/b/c/d/e/f",
        "largest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
    }
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/summary")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected = {
        "total_change_points": 1,
        "newest_time": 3,
        "newest_test_name": "a/b/c/d/e/f",
        "oldest_time": 3,
        "oldest_test_name": "a/b/c/d/e/f",
        "newest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "oldest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "largest_change": 100.0,
        "largest_test_name": "a/b/c/d/e/f",
        "largest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
    }
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/summary")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected = {
        "total_change_points": 1,
        "newest_time": 3,
        "newest_test_name": "a/b/c/d/e/f",
        "oldest_time": 3,
        "oldest_test_name": "a/b/c/d/e/f",
        "newest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "oldest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "largest_change": 100.0,
        "largest_test_name": "a/b/c/d/e/f",
        "largest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
    }
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/summary")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected = {
        "total_change_points": 1,
        "newest_time": 3,
        "newest_test_name": "a/b/c/d/e/f",
        "oldest_time": 3,
        "oldest_test_name": "a/b/c/d/e/f",
        "newest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "oldest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
        "largest_change": 100.0,
        "largest_test_name": "a/b/c/d/e/f",
        "largest_change_point": {
            "metric": "metric1",
            "index": 2,
            "time": 3,
            "forward_change_percent": "100",
            "magnitude": "1.000000",
            "mean_before": "1.000000",
            "stddev_before": "0.000000",
            "mean_after": "2.000000",
            "stddev_after": "0.000000",
            "pvalue": "0.000000",
        },
    }
    assert_response_data_matches_expected([json], [expected])
