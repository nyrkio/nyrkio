from backend.db.db import DBStore
from backend.github.runner import RunnerLauncher
from fastapi import APIRouter
from typing import Dict
from datetime import datetime, timezone
from fastapi import HTTPException
import logging
import httpx
import os
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
    store = DBStore()
    await store.log_json_event(gh_event, "GitHub App Webhook")

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

    if gh_event["action"] in ["queued"] and "workflow_job" in gh_event:
        target_org_or_repo = None
        if "organization" in gh_event:
            target_org_or_repo = gh_event["organization"]["login"]
        if "repository" in gh_event:
            target_org_or_repo = gh_event["repository"]["full_name"]

        repo_owner = target_org_or_repo.split("/")[0]

        nyrkio_user = store.get_user_by_github_username(repo_owner)
        # FIXME: Add a check for quota
        if not nyrkio_user:
            raise HTTPException(
                status_code=401,
                message="User {repo_owner} not found in Nyrkio. ({nyrkio_user})",
            )

        run_id = gh_event["workflow_job"]["run_id"]
        job_name = gh_event["workflow_job"]["name"]
        run_attempt = gh_event["workflow_job"]["run_attempt"]
        workflow_name = gh_event["workflow_job"]["workflow_name"]
        sender = gh_event["sender"]["login"]
        labels = gh_event["workflow_job"]["labels"]

        runs_on = labels.intersection(set(supported_instance_types()))

        if runs_on:
            await store.log_json_event(
                gh_event,
                "Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {target_org_or_repo} from {sender} with labels {labels} -> {runs_on}",
            )
            runner_registration_token = await get_github_runner_registration_token(
                org_name=repo_owner
            )
            launcher = RunnerLauncher(nyrkio_user.id, gh_event, runs_on.pop())
            await launcher.launch(runner_registration_token)
        elif labels:
            logger.info(
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {target_org_or_repo} from {sender} with labels {labels}, but no supported instance types found."
            )

    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}


# Get a one time token to register a new runner
async def get_github_runner_registration_token(org_name=None, repo_full_name=None):
    if repo_full_name:
        url = "https://api.github.com/repos/{repo_full_name}/actions/runners/registration-token"
    elif org_name:
        url = (
            "https://api.github.com/orgs/{org_name}/actions/runners/registration-token"
        )
    else:
        raise Exception("Either org_name or repo_full_name must be provided")

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
        runner_configuration_token = response.json()["token"]
        logging.debug("Got a runner_configuration_token {runner_configuration_token}")
    else:
        logging.info(
            f"Failed to fetch a runner_configuration_token: {response.status_code} {response.text}"
        )

    return runner_configuration_token
