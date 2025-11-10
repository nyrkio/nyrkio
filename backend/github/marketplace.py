import asyncio
from backend.db.db import DBStore
from backend.github.runner_configs import supported_instance_types
from backend.api.background import check_queued_workflow_jobs, filter_out_unsupported_jobs
from fastapi import APIRouter
from typing import Dict
from datetime import datetime, timezone
from fastapi import HTTPException
import logging

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
    return_message = None
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

        run_id = gh_event["workflow_job"]["run_id"]
        job_name = gh_event["workflow_job"]["name"]
        run_attempt = gh_event["workflow_job"]["run_attempt"]
        workflow_name = gh_event["workflow_job"]["workflow_name"]
        labels = gh_event["workflow_job"]["labels"]
        supported = supported_instance_types()
        runs_on = [lab for lab in labels if lab in supported]

        print(labels)
        print(runs_on)
        if runs_on:
            await store.log_json_event(gh_event, event_type="workflow_job")
            await store.log_json_event(
                {
                    "message": f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels} -> {runs_on}"
                },
                event_type="internal message",
            )
            await store.queue_work_task(gh_event, task_type="workflow_job")
            return_message = f"Queued a job to launch an instance of type {labels}"

        elif labels:
            logger.info(
                f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels}, but no supported instance types found."
            )
            return {
                "message": f"Got new workflow_job {workflow_name}/{job_name}/{run_id} (attempt {run_attempt}) for {repo_owner}/{repo_name} from {sender} with labels {labels}, but no supported instance types found.",
                "status": "nothing to do",
            }

    default_message = "Thank you for using Nyrkiö. For Faster Software!"
    return {
        "status": "success" if return_message else "nothing to do",
        "message": return_message if return_message else default_message,
    }


async def handle_pull_requests(gh_event):
    # We don't do anything with pull requests as such, but to minimize the list of permissions to ask for,
    # Use this to indirectly trigger things that you would normally get from workflow_job events.
    # Maybe one day I'll ask for those permissions. Just want to see this working first.
    if "pull_request" in gh_event and gh_event.get("action") in [
        "opened",
        "reopened",
        "edited",
        "synchronize",
        "labeled",
        "unlabeled",
    ]:
        repo_name = gh_event["pull_request"]["base"]["repo"]["full_name"]

        # Give GH some time to queue the jobs. And MySQL to async replicate them...
        await asyncio.sleep(7)
        queued_jobs = await check_queued_workflow_jobs(repo_name)
        queued_jobs = filter_out_unsupported_jobs(queued_jobs)
        # Needed to prevent infinite loops in valid cases. If this is reached,
        # github will 403 because you reached the maximum requests allowed per hour.
        max_loops = 7
        while queued_jobs and max_loops > 0:
            max_loops -= 1
            logger.info(
                f"Found {len(queued_jobs)} queued jobs for {repo_name} on PR event."
            )
            if len(queued_jobs) == 1:
                logger.info(
                    "Will sleep a minute and check again if more runners are still needed."
                )
                await asyncio.sleep(60)
                queued_jobs = await check_queued_workflow_jobs(repo_name)
                queued_jobs = filter_out_unsupported_jobs(queued_jobs)
                if not queued_jobs:
                    break

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
            logger.debug(fake_event)
            res = await _github_events(fake_event)
            # There can and will be several pull_request events, and handling the fake event could take a few minutes.
            # So we need to refresh the queue to ensure we don't start too many runners in multile parallel threads/coroutines.
            if isinstance(res, dict) and res.get("status") == "success":
                queued_jobs = await check_queued_workflow_jobs(repo_name)
                queued_jobs = filter_out_unsupported_jobs(queued_jobs)

        return queued_jobs
