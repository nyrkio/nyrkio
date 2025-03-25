import os
import requests
from backend.tests.test_api import assert_response_data_matches_expected

# Must include the protocol prefix and port number if not 80
HOST = os.environ.get("TEST_HOST", "http://localhost:8000")
JWT_TOKEN = os.environ.get("TEST_JWT_TOKEN")


class RestClient:
    def __init__(self):
        self.s = requests.Session()
        self.access_token = JWT_TOKEN
        self.headers = {}
        self.headers.update({"Content-type": "application/json"})

    def login(self, username=None, password=None):
        self.email = username if username is not None else "testuser@foo.com"
        self.password = password if password is not None else "somepass"
        print(self.headers)
        headers = {}
        headers.update(self.headers)
        # headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        resp = self.post(
            "/api/v0/auth/register",
            json={"email": self.email, "password": self.password},
            headers=headers,
        )
        json = resp.json()
        print(json)
        if json.get("detail") == "REGISTER_USER_ALREADY_EXISTS":
            # resp = self.post("/api/v0/auth/token",
            #                  json={"email": self.email, "password": self.password},
            #                  headers=headers)
            # json = resp.json()
            # print(json)
            # self.access_token = json["access_token"]
            # self.headers.update({'Authorization': 'Bearer '+self.access_token})
            return self.actual_login()

        resp.raise_for_status()
        self.access_token = json["access_token"]
        self.headers.update({"Authorization": "Bearer " + self.access_token})
        return self.actual_login()

    def actual_login(self):
        print(self.email, self.password)
        headers = {}
        headers.update(self.headers)
        headers.update({"Content-type": "application/x-www-form-urlencoded"})

        resp = self.post(
            "/api/v0/auth/jwt/login",
            data={"username": self.email, "password": self.password},
            headers=headers,
        )
        json = resp.json()
        print(json)
        resp.raise_for_status()
        self.access_token = json["access_token"]
        self.headers.update({"Authorization": "Bearer " + self.access_token})
        return resp

    def get(self, url, headers={}, **kw):
        long_url = HOST + url
        _headers = {}
        _headers.update(self.headers)
        if headers:
            _headers.update(headers)
        print(_headers)
        return self.s.get(long_url, headers=_headers, **kw)

    def post(self, url, headers={}, **kw):
        long_url = HOST + url
        _headers = {}
        _headers.update(self.headers)
        if headers:
            _headers.update(headers)
        print(_headers)
        return self.s.post(long_url, headers=_headers, **kw)

    def put(self, url, headers={}, **kw):
        long_url = HOST + url
        _headers = {}
        _headers.update(self.headers)
        if headers:
            _headers.update(headers)
        print(_headers)
        return self.s.put(long_url, headers=_headers, **kw)


def get_client():
    s = RestClient()
    return s

    # client = SuperuserClient(app)
    # client.login()
    # return client


def _generate_data(values, metric_name="metric1", unit="ms"):
    attr = {
        "git_repo": "https://github.com/nyrkio/nyrkio",
        "branch": "main",
        "git_commit": "123456",
    }
    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": -9999999999999, "unit": "ms"},
            ],
            "attributes": attr,
        },
        {
            "timestamp": 2,
            "metrics": [
                {"name": "metric1", "value": -9999999999999, "unit": "ms"},
            ],
            "attributes": attr,
        },
        {
            "timestamp": 3,
            "metrics": [
                {"name": "metric1", "value": -9999999999999, "unit": "ms"},
            ],
            "attributes": attr,
        },
        {
            "timestamp": 4,
            "metrics": [
                {"name": "metric1", "value": -9999999999999, "unit": "ms"},
            ],
            "attributes": attr,
        },
        {
            "timestamp": 5,
            "metrics": [
                {"name": "metric1", "value": -9999999999999, "unit": "ms"},
            ],
            "attributes": attr,
        },
    ]

    for d, v in zip(data, values):
        d["metrics"][0]["value"] = v

    return data


def test_one_deep_summary(client, username="albert@example.com"):
    """Upload multiple results, that include a change, then verify summary end point"""
    superuser_client = get_client()
    superuser_client.login(username=username)
    # client.login()
    client = superuser_client

    data = _generate_data([1.0, 1.0, 2.0, 2.0, 2.0])
    response = client.put("/api/v0/result/a/b/c/d/e/f", json=data)
    print(response.json())
    assert response.status_code == 200

    response = client.get("/api/v0/result/a/b/c/d/e/f/changes")
    assert response.status_code == 200
    json = response.json()
    print("changes: {}: {}".format(type(json), json))
    expected = {
        "a/b/c/d/e/f": [
            {
                "time": 3,
                "changes": [
                    {
                        "metric": "metric1",
                        "index": 2,
                        "time": 3,
                        "forward_change_percent": "100",
                        "magnitude": "1.000000",
                        "pvalue": "0.000000",
                    }
                ],
            }
        ]
    }

    assert_response_data_matches_expected([json], [expected])

    # superuser_client = SuperuserClient(app)
    # superuser_client.login()
    # TODO: Set this with pymongo directly (Or make this http end point go away, preferably)
    # This user needs to be superuser. Did it manually for now. Could edit MongoDB database directly with pymongo.
    response = superuser_client.get("/api/v0/results/precompute")
    print(response.json())
    assert response.status_code == 200

    # response = client.get("/api/v0/result/a/b/c/d/e/f/summarySiblings")
    # assert response.status_code == 200
    # json = response.json()
    # expected = [{}]
    # assert_response_data_matches_expected(json, expected)

    response = client.get("/api/v0/result/a/b/c/d/e/f/changes")
    assert response.status_code == 200
    json = response.json()
    print("changes: {}: {}".format(type(json), json))

    response = client.get("/api/v0/results")
    json = response.json()
    print(json)
    assert json[0]["test_name"] == "a/b/c/d/e/f"

    assert response.status_code == 200

    response = client.get("/api/v0/result/summarySiblings")
    json = response.json()
    print(json)
    response = client.get("/api/v0/result/foo/summarySiblings")
    json = response.json()
    print(json)
    response = client.get("/api/v0/result/a/b/summarySiblings")
    json = response.json()
    print(json)
    response = client.get("/api/v0/result/a/b/c/d/e/f")
    json = response.json()
    print(json)
    response = client.get("/api/v0/result/a/b/c/d/e/f/summarySiblings")
    json = response.json()
    print(json)

    response = client.get("/api/v0/result/a/b/c/d/e/summarySiblings")
    json = response.json()
    print(json)

    expected = {
        "a/b/c/d/e/f": {
            "largest_change": 100.0,
            "largest_change_point": {
                "forward_change_percent": "100",
                "index": 2,
                "magnitude": "1.000000",
                "pvalue": "0.000000",
                "time": 3,
            },
            "largest_test_name": "a/b/c/d/e/f",
            "oldest_change_point": {
                "forward_change_percent": "100",
                "index": 2,
                "magnitude": "1.000000",
                "pvalue": "0.000000",
                "time": 3,
            },
            "oldest_test_name": "a/b/c/d/e/f",
            "oldest_time": 3,
            "total_change_points": 1,
        }
    }

    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/d/summarySiblings")
    print(response.json())
    assert response.status_code == 200
    json = response.json()
    expected["a/b/c/d/e"] = expected["a/b/c/d/e/f"]
    del expected["a/b/c/d/e/f"]
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a/b/c/d"] = expected["a/b/c/d/e"]
    del expected["a/b/c/d/e"]
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a/b/c"] = expected["a/b/c/d"]
    del expected["a/b/c/d"]
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a/b"] = expected["a/b/c"]
    del expected["a/b/c"]
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a"] = expected["a/b"]
    del expected["a/b"]
    assert_response_data_matches_expected([json], [expected])


def test_treelike_hierarchy_summary(client, username="ebba@example.com"):
    """Upload multiple results, that include a change, then verify summary end point"""
    superuser_client = get_client()
    superuser_client.login(username=username)
    client = superuser_client

    data = _generate_data([1.0, 1.0, 1.0, 2.0, 2.0])
    data2 = _generate_data([100.0, 900.0, 900.0, 900.0, 900.0], metric_name="metric2")

    def post_results(testName, maybeData):
        dat = maybeData if maybeData else _generate_data([1.0] * 5)
        response = client.put("/api/v0/result/" + testName, json=dat)
        print(vars(response))
        assert response.status_code == 200
        return response

    testName = "a/b/c/d/e/f"
    response = post_results(testName, data)
    testName = "abraham/beth/carl/david/emil/farao"
    response = post_results(testName, data2)
    testName = "a/b/c/d/emil/farao"
    response = post_results(testName, data2)
    #############################################################
    response = superuser_client.get("/api/v0/results/precompute")
    print(vars(response))
    assert response.status_code == 200
    #############################################################

    # response = client.get("/api/v0/result/a/b/c/d/e/f/summarySiblings")
    # assert response.status_code == 200
    # json = response.json()
    # expected = [{}]
    # assert_response_data_matches_expected(json, expected)

    response = client.get("/api/v0/result/a/b/c/d/e/summarySiblings")
    print(response.json())
    assert response.status_code == 200
    json = response.json()
    expected = {
        "a/b/c/d/e/f": {
            "largest_change": 100.0,
            "largest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "largest_test_name": "a/b/c/d/e/f",
            "newest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "newest_test_name": "a/b/c/d/e/f",
            "newest_time": 4,
            "oldest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "oldest_test_name": "a/b/c/d/e/f",
            "oldest_time": 4,
            "total_change_points": 1,
        }
    }

    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/d/summarySiblings")
    print(response.json())
    assert response.status_code == 200
    json = response.json()
    expected = {
        "a/b/c/d/e": {
            "largest_change": 100.0,
            "largest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "largest_test_name": "a/b/c/d/e/f",
            "newest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "newest_test_name": "a/b/c/d/e/f",
            "newest_time": 4,
            "oldest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "mean_after": "2.000000",
                "mean_before": "1.000000",
                "metric": "metric1",
                "pvalue": "0.000000",
                "stddev_after": "0.000000",
                "stddev_before": "0.000000",
                "time": 4,
            },
            "oldest_test_name": "a/b/c/d/e/f",
            "oldest_time": 4,
            "total_change_points": 1,
        },
        "a/b/c/d/emil": {
            "largest_change": 800.0,
            "largest_change_point": {
                "forward_change_percent": "800",
                "index": 1,
                "magnitude": "8.000000",
                "mean_after": "900.000000",
                "mean_before": "100.000000",
                "metric": "metric1",
                "time": 2,
            },
            "largest_test_name": "a/b/c/d/emil/farao",
            "newest_change_point": {
                "forward_change_percent": "800",
                "index": 1,
                "magnitude": "8.000000",
                "mean_after": "900.000000",
                "mean_before": "100.000000",
                "metric": "metric1",
                "time": 2,
            },
            "newest_test_name": "a/b/c/d/emil/farao",
            "newest_time": 2,
            "oldest_change_point": {
                "forward_change_percent": "800",
                "index": 1,
                "magnitude": "8.000000",
                "mean_after": "900.000000",
                "mean_before": "100.000000",
                "metric": "metric1",
                "time": 2,
            },
            "oldest_test_name": "a/b/c/d/emil/farao",
            "oldest_time": 2,
            "total_change_points": 1,
        },
    }

    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/c/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected = {
        "a/b/c/d": {
            "largest_change": 800.0,
            "largest_change_point": {
                "forward_change_percent": "800",
                "index": 1,
                "magnitude": "8.000000",
                "mean_after": "900.000000",
                "metric": "metric1",
                "time": 2,
            },
            "largest_test_name": "a/b/c/d/emil/farao",
            "newest_change_point": {
                "forward_change_percent": "100",
                "index": 3,
                "magnitude": "1.000000",
                "metric": "metric1",
                "time": 4,
            },
            "newest_test_name": "a/b/c/d/e/f",
            "newest_time": 4,
            "oldest_change_point": {
                "forward_change_percent": "800",
                "index": 1,
                "magnitude": "8.000000",
                "mean_after": "900.000000",
                "metric": "metric1",
                "time": 2,
            },
            "oldest_test_name": "a/b/c/d/emil/farao",
            "oldest_time": 2,
            "total_change_points": 2,
        }
    }
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/b/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a/b/c"] = expected["a/b/c/d"]
    del expected["a/b/c/d"]
    assert_response_data_matches_expected([json], [expected])

    response = client.get("/api/v0/result/a/summarySiblings")
    print(vars(response))
    assert response.status_code == 200
    json = response.json()
    expected["a/b"] = expected["a/b/c"]
    del expected["a/b/c"]
    assert_response_data_matches_expected([json], [expected])
