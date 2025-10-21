from unittest.mock import AsyncMock, patch
from backend.tests.test_challenge_publish import (
    _get_claim,
    _get_mocked_github_responses1,
    _get_mocked_github_responses2,
)


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("backend.core.core.cached_get")
def test_public_org_pr_cph_notify(
    mock_sieve,
    mock_httpx_client_get,
    mock_httpx_client_post,
    unauthenticated_client,
    gh_client,
):
    mock_sieve.side_effect = lambda repo, commit: commit
    # For orgs, the test_name prefix must match the repo_owner/repo_name and even branch
    add_public_results(
        "nyrkio2/tools/main/benchmark1", gh_client, unauthenticated_client
    )

    cph_creds, sessionplus = do_cph_auth(
        mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client
    )

    headers = {"Authorization": "Bearer {}".format(cph_creds["jwt_token"])}

    pull_number = 123
    repo = "nyrkio2/tools"
    data = {
        "timestamp": 34,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12345666",
        },
        "extra_info": {},
    }

    response = gh_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    assert json == [
        {
            "pull_number": pull_number,
            "test_names": ["benchmark1"],
            "git_commit": "12345666",
            "git_repo": "https://github.com/nyrkio2/tools",
            "branch": "main",
        }
    ]

    data2 = {
        "timestamp": 39,
        "metrics": [
            {"name": "metric1", "value": 999.9, "unit": "ms"},
            {"name": "metric2", "value": 2.5, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12349999",
        },
        "extra_info": {},
    }
    # This is what we're here for.
    print("----- Now the test starts ------")
    response = unauthenticated_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/nyrkio2/tools/main/benchmark1",
        json=[data2],
        headers=headers,
    )
    assert response.status_code == 200

    last_commit = "12349999"

    response = unauthenticated_client.get(
        f"/api/v0/public/pulls/{repo}/{pull_number}/changes/{last_commit}/test/nyrkio2/tools/main/benchmark1",
        headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    assert json == [
        {
            "nyrkio2/tools/main/benchmark1": [
                {
                    "time": 39,
                    "attributes": {
                        "git_commit": "12349999",
                        "branch": "main",
                        "git_repo": "https://github.com/nyrkio2/tools",
                        "commit_msg": "12349999",
                    },
                    "changes": [
                        {
                            "metric": "metric1",
                            "index": 4,
                            "time": 39,
                            "forward_change_percent": "92914",
                            "magnitude": "929.139535",
                            "mean_before": "1.075000",
                            "stddev_before": "0.082916",
                            "mean_after": "999.900000",
                            "stddev_after": "0.000000",
                            "pvalue": "0.000000",
                        }
                    ],
                }
            ]
        }
    ]
    response = unauthenticated_client.get(
        f"/api/v0/public/pulls/{repo}/{pull_number}/changes/{last_commit}/test/nyrkio2/tools/main/benchmark1?notify=1",
        headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("backend.core.core.cached_get")
def test_public_user_pr_cph_notify(
    mock_sieve,
    mock_httpx_client_get,
    mock_httpx_client_post,
    unauthenticated_client,
    gh_client,
):
    mock_sieve.side_effect = lambda repo, commit: commit
    pull_number = 123
    repo = "ghuser/tools"
    add_public_results("benchmark1", gh_client, unauthenticated_client, repo)

    cph_creds, sessionplus = do_cph_auth(
        mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client, repo
    )

    headers = {"Authorization": "Bearer {}".format(cph_creds["jwt_token"])}

    data = {
        "timestamp": 34,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12345666",
        },
        "extra_info": {},
    }

    response = gh_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    assert json == [
        {
            "pull_number": pull_number,
            "test_names": ["benchmark1"],
            "git_commit": "12345666",
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
        }
    ]

    data2 = {
        "timestamp": 39,
        "metrics": [
            {"name": "metric1", "value": 999.9, "unit": "ms"},
            {"name": "metric2", "value": 2.5, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12349999",
        },
        "extra_info": {},
    }
    # This is what we're here for.
    print("----- Now the test starts ------")
    response = unauthenticated_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1",
        json=[data2],
        headers=headers,
    )
    assert response.status_code == 200

    last_commit = "12349999"

    response = unauthenticated_client.get(
        f"/api/v0/public/pulls/{repo}/{pull_number}/changes/{last_commit}/test/ghuser/tools/main/benchmark1",
        headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    # print(json)
    assert len(json) == 1

    assert json == [
        {
            "benchmark1": [
                {
                    "time": 39,
                    "attributes": {
                        "git_commit": "12349999",
                        "branch": "main",
                        "git_repo": "https://github.com/ghuser/tools",
                        "commit_msg": "12349999",
                    },
                    "changes": [
                        {
                            "metric": "metric1",
                            "index": 4,
                            "time": 39,
                            "forward_change_percent": "92914",
                            "magnitude": "929.139535",
                            "mean_before": "1.075000",
                            "stddev_before": "0.082916",
                            "mean_after": "999.900000",
                            "stddev_after": "0.000000",
                            "pvalue": "0.000000",
                        }
                    ],
                }
            ]
        }
    ]
    response = unauthenticated_client.get(
        f"/api/v0/public/pulls/{repo}/{pull_number}/changes/{last_commit}/test/ghuser/tools/main/benchmark1?notify=1",
        headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    # print(json)
    assert len(json) == 1


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("backend.core.core.cached_get")
def test_public_user_fail_pr_cph_notify(
    mock_sieve,
    mock_httpx_client_get,
    mock_httpx_client_post,
    unauthenticated_client,
    gh_client,
):
    mock_sieve.side_effect = lambda repo, commit: commit
    pull_number = 123
    repo = "ghuser/tools"
    add_public_results("benchmark1", gh_client, unauthenticated_client, repo)

    repo = "nyrkio2/tools"
    cph_creds, sessionplus = do_cph_auth(
        mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client, repo
    )

    headers = {"Authorization": "Bearer {}".format(cph_creds["jwt_token"])}
    repo = "ghuser/tools"

    data = {
        "timestamp": 34,
        "metrics": [
            {"name": "metric1", "value": 1.0, "unit": "ms"},
            {"name": "metric2", "value": 2.0, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12345666",
        },
        "extra_info": {},
    }

    response = gh_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1", json=[data]
    )
    assert response.status_code == 200

    response = gh_client.get("/api/v0/pulls")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1

    assert json == [
        {
            "pull_number": pull_number,
            "test_names": ["benchmark1"],
            "git_commit": "12345666",
            "git_repo": "https://github.com/ghuser/tools",
            "branch": "main",
        }
    ]

    data2 = {
        "timestamp": 39,
        "metrics": [
            {"name": "metric1", "value": 999.9, "unit": "ms"},
            {"name": "metric2", "value": 2.5, "unit": "ms"},
        ],
        "attributes": {
            "git_repo": "https://github.com/" + repo,
            "branch": "main",
            "git_commit": "12349999",
        },
        "extra_info": {},
    }
    # This is what we're here for.
    print("----- Now the test starts ------")
    response = unauthenticated_client.post(
        f"/api/v0/pulls/{repo}/{pull_number}/result/benchmark1",
        json=[data2],
        headers=headers,
    )

    # Trying to post against a repo that isn't in the org that we first authenticated against with CPH, is not permitted
    assert response.status_code == 403


def add_public_results(test_name, client, unauthenticated_client, repo="nyrkio2/tools"):
    client.login()

    data = [
        {
            "timestamp": 1,
            "metrics": [
                {"name": "metric1", "value": 1.1, "unit": "ms"},
                {"name": "metric2", "value": 2.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 11,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 2.1, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "123466",
            },
        },
        {
            "timestamp": 22,
            "metrics": [
                {"name": "metric1", "value": 1.2, "unit": "ms"},
                {"name": "metric2", "value": 5.0, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "123476",
            },
        },
        {
            "timestamp": 33,
            "metrics": [
                {"name": "metric1", "value": 1.0, "unit": "ms"},
                {"name": "metric2", "value": 4.8, "unit": "ms"},
            ],
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
                "git_commit": "123488",
            },
        },
    ]
    url = f"/api/v0/result/{test_name}"
    if test_name.startswith("nyrkio2/"):
        url = f"/api/v0/orgs/result/{test_name}"

    response = client.post(url, json=data)

    assert response.status_code == 200

    response = client.get(f"/api/v0/config/{test_name}")
    assert response.status_code == 200
    data = response.json()
    assert not data

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/" + repo,
                "branch": "main",
            },
        }
    ]

    url = f"/api/v0/config/{test_name}"
    if test_name.startswith("nyrkio2/"):
        url = f"/api/v0/orgs/config/{test_name}"

    response = client.post(url, json=config)
    assert response.status_code == 200

    response = client.get(url)
    assert response.status_code == 200
    assert response.json()[0]["public"] is True

    response = unauthenticated_client.get("/api/v0/public/results")
    assert response.status_code == 200
    json = response.json()
    # Note: in public/ api the org/repo/branch are always there. System adds them as needed.
    assert json == [
        {
            "test_name": repo + "/main/benchmark1",
        }
    ]

    # Test first without the cph creds, this is random anonymous internet user
    response = unauthenticated_client.get(
        f"/api/v0/public/result/{repo}/main/benchmark1"
    )
    assert response.status_code == 200


def do_cph_auth(
    mock_httpx_client_get,
    mock_httpx_client_post,
    unauthenticated_client,
    repo="nyrkio2/tools",
):
    claim = _get_claim(repo)
    artifact_id = 567
    repo_owner, repo_name = repo.split("/")
    mock_responses = _get_mocked_github_responses1(claim, artifact_id)
    mock_httpx_client_get.return_value = mock_responses["claim_200"]
    mock_httpx_client_post.return_value = mock_responses["claim_200"]
    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/claim", json=claim.model_dump(mode="json")
    )

    assert response.status_code == 200
    challenge = response.json()
    assert challenge["session"]["username"] == "mock_github_identity"
    assert challenge["session"]["client_secret"] == claim.client_secret
    assert challenge["session"]["repo_owner"] == claim.repo_owner
    assert challenge["session"]["server_secret"]  # It's a uuid, if you want to know
    assert challenge["claimed_identity"]["username"] == "mock_github_identity"

    handshake_complete = {
        "session": {
            "username": "mock_github_identity",
            "client_secret": "random_secret_from_client",
            "repo_owner": repo_owner,
            "server_secret": challenge["session"]["server_secret"],
        },
        "artifact_id": artifact_id,
    }

    mock_responses = _get_mocked_github_responses2(
        claim, artifact_id, challenge["public_challenge"]
    )
    mock_httpx_client_get.return_value = mock_responses["complete_200"]
    mock_httpx_client_post.return_value = mock_responses["complete_200"]
    # print(mock_responses["complete_200"])

    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/complete", json=handshake_complete
    )
    complete = response.json()
    # print(complete)
    assert response.status_code == 200

    assert complete["github_username"] == "mock_github_identity"
    assert complete["jwt_token"]
    return complete, handshake_complete
