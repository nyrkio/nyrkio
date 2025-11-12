import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from backend.github.runner import check_work_queue
from backend.api.background import old_background_worker


@patch("backend.github.runner.get_github_runner_registration_token")
@patch("backend.github.runner.RunnerLauncher.launch")
def test_work_queue(mock_get_token, mock_launcher, client, superuser_client):
    """Put a task onto the work queue, then get it back."""
    mock_launcher.return_value = AsyncMock()

    client.login()

    data = _new_input_doc()

    response = client.post("/api/v0/github/webhook", json=data)
    assert response.status_code == 200
    print(response.json())

    superuser_client.login()
    # response = superuser_client.get("/api/v0/results/precompute")
    response = asyncio.run(old_background_worker())

    r = response
    print(r)
    assert r["task"][r["task_type"]]["run_id"] == 1234

    mock_get_token.assert_called_once_with()
    mock_launcher.assert_called_once_with(
        org_name="ghuser2" installation_id=6666, repo_full_name="ghuser2/reponame"
    )


def _new_input_doc(
    github_username="ghuser2",
    run_id=1234,
    run_attempt=1,
    installation_id=6666,
    reponame="reponame",
):
    return {
        "action": "queued",
        "workflow_job": {
            "run_id": run_id,
            "name": "unit test dummy workflow",
            "run_attempt": run_attempt,
            "workflow_name": "Workflow name",
            "labels": ["nyrkio_perf_server_2cpu_ubuntu2404"],
        },
        "repository": {"owner": {"login": github_username}, "name": reponame},
        "sender": {"login": github_username},
        "installation": {"id": installation_id},
    }


@pytest.mark.asyncio
@patch("backend.github.runner.get_github_runner_registration_token")
@patch("backend.github.runner.RunnerLauncher.launch")
async def test_many_tasks_work_queue(mock_get_token, mock_launcher, client):
    """Add multiple tasks on to work queue, get them back in fifo order"""
    mock_launcher.return_value = AsyncMock()

    client.login()

    for i in range(0, 5):
        data = _new_input_doc(run_id=i)
        response = client.post("/api/v0/github/webhook", json=data)
        assert response.status_code == 200

    for i in range(0, 5):
        done_task = await check_work_queue()
        assert done_task["task"][done_task["task_type"]]["run_id"] == i

    none_task = await check_work_queue()
    assert none_task is None
