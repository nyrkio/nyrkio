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
        sender = gh_event["sender"]["login"]
        org_name = None
        if "organization" in gh_event and gh_event["organization"]:
            org_name = gh_event["organization"]["login"]
        logger.info(
            f"Workflow job for ({org_name}/{repo_owner}/{repo_name}) triggered by {sender}"
        )

        # repo_owner is either the user or an org
        nyrkio_user = await store.get_user_by_github_username(repo_owner)
        nyrkio_org = None
        if nyrkio_user is not None:
            nyrkio_user = nyrkio_user.id
        else:
            nyrkio_user = await store.get_user_by_github_username(sender)
            if nyrkio_user is not None:
                nyrkio_user = nyrkio_user.id

        if org_name:
            nyrkio_org = await store.get_org_by_github_org(org_name, sender)
            if nyrkio_org is not None:
                nyrkio_org = nyrkio_org["organization"]["id"]

        # FIXME: Add a check for quota
        if (not nyrkio_user) and (not nyrkio_org):
            logger.warning(f"User {repo_owner} not found in Nyrkio. ({nyrkio_user})")
            raise HTTPException(
                status_code=401,
                detail="None of {org_name}/{repo_owner}/{sender} were found in Nyrkio. ({nyrkio_org}/{nyrkio_user})",
            )

        nyrkio_billing_user = nyrkio_org if nyrkio_org else nyrkio_user
        run_id = gh_event["workflow_job"]["run_id"]
        job_name = gh_event["workflow_job"]["name"]
        run_attempt = gh_event["workflow_job"]["run_attempt"]
        workflow_name = gh_event["workflow_job"]["workflow_name"]
        installation_id = gh_event["installation"]["id"]
        labels = gh_event["workflow_job"]["labels"]
        supported = supported_instance_types()
        runs_on = [lab for lab in labels if lab in supported]

        if runs_on:
            await store.log_json_event(
                gh_event,
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels} -> {runs_on}",
            )
            runner_registration_token = await get_github_runner_registration_token(
                org_name=org_name,
                installation_id=installation_id,
                repo_full_name=f"{repo_owner}/{repo_name}",
            )
            # Note: suppoorted_instance_types() and therefore also runs_on is ordered by preference. We take the first one.
            launcher = RunnerLauncher(
                nyrkio_user,
                nyrkio_org,
                nyrkio_billing_user,
                gh_event,
                runs_on.pop(),
                registration_token=runner_registration_token,
            )
            await launcher.launch()
        elif labels:
            logger.info(
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels}, but no supported instance types found."
            )

    return {"success": "Thank you for using Nyrkiö. For Faster Software!"}


# Get a one time token to register a new runner
async def get_github_runner_registration_token(
    org_name=None, repo_full_name=None, installation_id=None
):
    token = await fetch_access_token(
        token_url=None, expiration_seconds=600, installation_id=installation_id
    )
    if token:
        logging.info(
            f"Successfully fetched access token for installation_id {installation_id} at {repo_full_name}"
        )
    else:
        logging.info(
            f"Failed to fetch a app installation access token from GitHub for {repo_full_name}/{installation_id}. I can't deploy a runner without it."
        )
        raise Exception(
            f"Failed to fetch a app installation access token from GitHub for {repo_full_name}/{installation_id}. I can't deploy a runner without it."
        )

    client = httpx.AsyncClient()
    response = await client.post(
        f"https://api.github.com/orgs/{org_name}/actions/runners/registration-token",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code in [200, 201]:
        logging.debug(
            "Geting a runner registration token from github mothership succeeded. Now onto deploy some VMs."
        )
        return response.json()["token"]
    else:
        logging.info(
            f"Failed to fetch a runner_configuration_token from GitHub for {org_name}. I can't deploy a runner without it."
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
    elif response.status_code == 404:
        # On Github this means private repo and we don't have access
        return []
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
                "repository": gh_event["repository"],
                "organization": gh_event.get("organization", None),
                "sender": gh_event["sender"],
                "installation": gh_event.get("installation", None),
            }
            logger.info(fake_event)
            await _github_events(fake_event)
            # There can and will be several pull_request events, and handling the fake event could take a few minutes.
            # So we need to refresh the queue to ensure we don't start too many runners in multile parallel threads/coroutines.
            queued_jobs = await check_queued_workflow_jobs(repo_name)
        return queued_jobs
