import json
from backend.auth.challenge_publish import (
    ChallengePublishClaim,
)

from unittest.mock import MagicMock, AsyncMock, patch


def _get_claim(repo="nyrkio2/tools"):
    repo_owner, repo_name = repo.split("/")
    return ChallengePublishClaim(
        username="mock_github_identity",
        client_secret="random_secret_from_client",
        repo_owner=repo_owner,
        repo_name=repo_name,
        repo_owner_email="admin@nyrkio2.com",
        repo_owner_full_name="firstname lastname",
        workflow_name="mock_workflow",
        event_name="pull_request",
        run_number=1,
        run_id=12345,
        run_attempt=1,
    )


def _get_mocked_github_responses1(claim, artifact_id):
    return_responses = {}
    response_session = claim.model_dump(mode="json")
    response_session["server_secret"] = "mock_server_secret"
    resp_json = {
        "event": "pull_request",
        "actor": {"login": "mock_github_identity"},
        "session": response_session,
        "claimed_identity": {"username": "mock_github_identity"},
        "run_attempt": 1,
    }

    magic_response = MagicMock()
    magic_response.status_code = 200
    magic_response.json.return_value = resp_json
    return_responses["claim_200"] = magic_response

    response_session = claim.model_dump(mode="json")
    response_session["server_secret"] = "mock_server_secret"
    resp_json = {
        "event": "pull_request",
        "actor": {"login": "some_other_github_identity"},
        "session": response_session,
        "claimed_identity": {"username": "mock_github_identity"},
        "run_attempt": 1,
    }

    magic_response = MagicMock()
    magic_response.status_code = 200
    magic_response.json.return_value = resp_json
    return_responses["claim_401"] = magic_response

    magic_response = MagicMock()
    magic_response.status_code = 404
    magic_response.json.return_value = resp_json
    return_responses["claim_424"] = magic_response

    return return_responses


def _get_mocked_github_responses2(claim, artifact_id, public_challenge):
    _ = claim  # Not used here anymore
    return_responses = {}
    wrong_attachment = {
        "id": 666 + artifact_id,  # Anything but artifact_id
        "name": "some_log.txt",
    }
    correct_attachment = {
        "id": artifact_id,
        "name": "ChallengePublishHandshake." + public_challenge,
    }

    magic_response2 = MagicMock()
    magic_response2.status_code = 200
    magic_response2.json.return_value = {
        "artifacts": [wrong_attachment, correct_attachment]
    }
    return_responses["complete_200"] = magic_response2

    magic_response2 = MagicMock()
    magic_response2.status_code = 200
    magic_response2.json.return_value = {"artifacts": [wrong_attachment]}
    return_responses["complete_401"] = magic_response2
    return return_responses


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_challenge_publish_simple(
    mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client
):
    claim = _get_claim()
    artifact_id = 567
    mock_responses = _get_mocked_github_responses1(claim, artifact_id)
    mock_httpx_client_get.return_value = mock_responses["claim_200"]
    mock_httpx_client_post.return_value = mock_responses["claim_200"]
    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/claim", json=claim.model_dump(mode="json")
    )

    assert response.status_code == 200
    challenge = response.json()
    print("Challenge returned from mock http server")
    print(json.dumps(challenge, indent=4))
    # {
    #   'session': {
    #       'username': 'mock_github_identity',
    #       'client_secret': 'random_secret_from_client',
    #       'repo_owner': 'nyrkio2',
    #       'server_secret': '9dbe2105-acd2-4f2f-98c1-42fc2a272be5'
    #   },
    #   'public_challenge': 'bdfebc5b-baab-4bf7-b2cc-4b988e6d6eed',
    #   'artifact_id': None,
    #   'public_message': 'ChallengePublishHandshake between github.com and nyrkio.com:\nI am mock_github_identity and this is proof that I am currently running /nyrkio2/tools/actions/runs/12345: bdfebc5b-baab-4bf7-b2cc-4b988e6d6eed',
    #   'claimed_identity': {'username': 'mock_github_identity', 'client_secret': 'random_secret_from_client', 'repo_owner': 'nyrkio2', 'repo_name': 'tools', 'repo_owner_email': 'admin@nyrkio2.com', 'repo_owner_full_name': 'firstname lastname', 'workflow_name': 'mock_workflow', 'event_name': 'pull_request', 'run_number': 1, 'run_id': 12345, 'run_attempt': 1
    #   }
    # }

    assert challenge["session"]["username"] == "mock_github_identity"
    assert challenge["session"]["client_secret"] == claim.client_secret
    assert challenge["session"]["repo_owner"] == claim.repo_owner
    assert challenge["session"]["server_secret"]  # It's a uuid, if you want to know
    assert challenge["claimed_identity"]["username"] == "mock_github_identity"

    handshake_complete = {
        "session": {
            "username": "mock_github_identity",
            "client_secret": "random_secret_from_client",
            "repo_owner": "nyrkio2",
            "server_secret": challenge["session"]["server_secret"],
        },
        "artifact_id": artifact_id,
    }

    from backend.auth.challenge_publish import handshake_ongoing_map

    print(handshake_ongoing_map)
    mock_responses = _get_mocked_github_responses2(
        claim, artifact_id, challenge["public_challenge"]
    )
    mock_httpx_client_get.return_value = mock_responses["complete_200"]
    mock_httpx_client_post.return_value = mock_responses["complete_200"]
    print(mock_responses["complete_200"])

    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/complete", json=handshake_complete
    )
    complete = response.json()
    print(complete)
    assert response.status_code == 200

    assert complete["github_username"] == "mock_github_identity"
    assert complete["jwt_token"]


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_challenge_publish_fail_user(
    mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client
):
    claim = _get_claim()
    artifact_id = 567
    mock_responses = _get_mocked_github_responses1(claim, artifact_id)
    mock_httpx_client_get.return_value = mock_responses["claim_401"]
    mock_httpx_client_post.return_value = mock_responses["claim_401"]
    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/claim", json=claim.model_dump(mode="json")
    )

    assert response.status_code == 401


@patch("backend.auth.challenge_publish.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("backend.auth.challenge_publish.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_challenge_publish_fail_attachment(
    mock_httpx_client_get, mock_httpx_client_post, unauthenticated_client
):
    claim = _get_claim()
    artifact_id = 567
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
            "repo_owner": "nyrkio2",
            "server_secret": challenge["session"]["server_secret"],
        },
        "artifact_id": artifact_id,
    }

    mock_responses = _get_mocked_github_responses2(
        claim, artifact_id, challenge["public_challenge"]
    )
    mock_httpx_client_get.return_value = mock_responses["complete_401"]
    mock_httpx_client_post.return_value = mock_responses["complete_401"]

    response = unauthenticated_client.post(
        "/api/v0/challenge_publish/github/complete", json=handshake_complete
    )
    assert response.status_code == 401
