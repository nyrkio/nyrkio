from backend.db.db import DBStore
from backend.github.runner import RunnerLauncher
from fastapi import APIRouter
from typing import Dict
from datetime import datetime, timezone
from fastapi import HTTPException
import logging
import httpx
import os
from backend.notifiers.github import fetch_access_token
from backend.github.runner_configs import supported_instance_types

logger = logging.getLogger(__file__)


github_router = APIRouter(prefix="/github")


@github_router.post("/marketplace-events")
async def marketplace_events(gh_event: Dict):
    store = DBStore()
    await store.log_json_event(gh_event, "GitHub Marketplace Webhook")
    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}


@github_router.post("/webhook")
async def github_events(gh_event: Dict):
    return await _github_events(gh_event)


async def _github_events(gh_event: Dict):
    store = DBStore()
    await store.log_json_event(gh_event, "GitHub App Webhook")

    await handle_pull_requests(gh_event)

    if gh_event["action"] in ["created"]:
        gh_id = gh_event["installation"]["account"]["id"]
        await store.set_github_installation(gh_id, gh_event)
    if gh_event["action"] in ["deleted"]:
        gh_id = gh_event["installation"]["account"]["id"]
        await store.set_github_installation(
            gh_id,
            {
                "nyrkio_status": "deleted",
                "nyrkio_datetime": datetime.now(tz=timezone.utc),
            },
        )

    # Would need more permissions on github
    # I will rather trigger this from the pull_request events that we already get
    if gh_event["action"] in ["queued"] and "workflow_job" in gh_event:
        repo_owner = gh_event["repository"]["owner"]["login"]
        repo_name = gh_event["repository"]["name"]
        logger.info(f"Workflow job for ({repo_owner}/{repo_name})")

        nyrkio_user = await store.get_user_by_github_username(repo_owner)
        # FIXME: Add a check for quota
        if not nyrkio_user:
            raise HTTPException(
                status_code=401,
                detail="User {repo_owner} not found in Nyrkio. ({nyrkio_user})",
            )

        run_id = gh_event["workflow_job"]["run_id"]
        job_name = gh_event["workflow_job"]["name"]
        run_attempt = gh_event["workflow_job"]["run_attempt"]
        workflow_name = gh_event["workflow_job"]["workflow_name"]
        sender = gh_event["sender"]["login"]
        labels = gh_event["workflow_job"]["labels"]
        supported = supported_instance_types()
        runs_on = [lab for lab in labels if lab in supported]

        if runs_on:
            await store.log_json_event(
                gh_event,
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels} -> {runs_on}",
            )
            runner_registration_token = await get_github_runner_registration_token(
                org_name=repo_owner
            )
            # Note: suppoorted_instance_types() and therefore also runs_on is ordered by preference. We take the first one.
            launcher = RunnerLauncher(nyrkio_user.id, gh_event, runs_on.pop())
            await launcher.launch(runner_registration_token)
        elif labels:
            logger.info(
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels}, but no supported instance types found."
            )

    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}


# Get a one time token to register a new runner
async def get_github_runner_registration_token(org_name=None, repo_full_name=None):
    url = None
    if repo_full_name:
        url = f"https://api.github.com/repos/{repo_full_name}/actions/runners/registration-token"
    elif org_name:
        url = (
            f"https://api.github.com/orgs/{org_name}/actions/runners/registration-token"
        )
    else:
        raise Exception("Either org_name or repo_full_name must be provided")

    client = httpx.AsyncClient()
    token = await fetch_access_token(url, 3600)
    response = await client.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            # "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if response.status_code <= 201:
        runner_configuration_token = response.json()["token"]
        logging.debug("Got a runner_configuration_token {runner_configuration_token}")
        return runner_configuration_token
    else:
        logging.info(
            f"Failed to fetch a runner_configuration_token: {response.status_code} {response.text}"
        )
        raise Exception(
            f"Failed to fetch a runner_configuration_token from GitHub for {org_name}. I can't deploy a runner without it."
        )


async def check_queued_workflow_jobs(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/actions/runs?status=queued"
    client = httpx.AsyncClient()
    token = os.environ["GITHUB_TOKEN"]
    response = await client.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            # "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if response.status_code <= 201:
        runs = response.json().get("workflow_runs", [])
        queued_jobs = []
        for run in runs:
            run_id = run["id"]
            jobs_url = f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/jobs"
            jobs_response = await client.get(
                jobs_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    # "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            if jobs_response.status_code <= 201:
                jobs = jobs_response.json().get("jobs", [])
                for job in jobs:
                    if job["status"] == "queued":
                        queued_jobs.append(job)
            else:
                logging.warning(
                    f"Failed to fetch jobs for run {run_id}: {jobs_response.status_code} {jobs_response.text}"
                )
        return queued_jobs
    else:
        logging.warning(
            f"Failed to fetch workflow runs: {response.status_code} {response.text}"
        )
        return []


async def handle_pull_requests(gh_event):
    # We don't do anything with pull requests as such, but to minimize the list of permissions to ask for,
    # Use this to indirectly trigger things that you would normally get from workflow_job events.
    # Maybe one day I'll ask for those permissions. Just want to see this working first.
    if "pull_request" in gh_event and gh_event.get("action") in [
        "opened",
        "reopened",
        "edited",
        "synchronize",
    ]:
        repo_name = gh_event["pull_request"]["base"]["repo"]["full_name"]

        queued_jobs = await check_queued_workflow_jobs(repo_name)
        while queued_jobs:
            logger.info(
                f"Found {len(queued_jobs)} queued jobs for {repo_name} on PR event."
            )
            job = queued_jobs.pop()
            # Call myself recursively, but with a fake workflow_job event
            fake_event = {
                "action": "queued",
                "workflow_job": job,
                "repository": gh_event["pull_request"]["base"]["repo"],
                "organization": gh_event["pull_request"]["base"]["repo"]["owner"],
                "sender": gh_event["sender"],
            }
            logger.info(fake_event)
            await _github_events(fake_event)
            # There can and will be several pull_request events, and handling the fake event could take a few minutes.
            # So we need to refresh the queue to ensure we don't start too many runners in multile parallel threads/coroutines.
            queued_jobs = await check_queued_workflow_jobs(repo_name)
        return queued_jobs
