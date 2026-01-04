import logging
import httpx
import asyncio
import os

from datetime import datetime
from backend.api.changes import _calc_changes
from backend.db.db import DBStore
from backend.github.runner import (
    workflow_job_event,
    check_work_queue,
    fetch_access_token,
)
from backend.github.runner_configs import supported_instance_types
from backend.aws.s3download import get_latest_runner_usage
from backend.api.metered import generate_unique_nyrkio_id, report_cpu_hours_consumed

logger = logging.getLogger(__file__)


async def old_background_worker():
    done_work = await check_work_queue()
    if done_work is not None:
        done_work["_id"] = str(done_work["_id"])
        return done_work


async def background_worker():
    for _ in range(15):
        if not await check_runner_usage():
            break

    done_work = await loop_installations()
    if len(done_work) > 0:
        logger.info(f"Background worker returned with {len(done_work)} messages.")
        for runner in done_work:
            logger.info(runner)

        return len(done_work)

    return await precompute_cached_change_points()


async def check_runner_usage():
    logger.info("check_runner_usage() data from s3")
    store = DBStore()
    latest_usage_report = await store.get_latest_runner_report()
    raw_line_items, latest_usage_report = await get_latest_runner_usage(
        seen_previously=latest_usage_report
    )
    logger.debug(str(raw_line_items))
    logger.debug(str(latest_usage_report))
    if raw_line_items:
        for user_id, user_raw_usage in raw_line_items.items():
            if user_raw_usage:
                await store.add_user_runner_usage_raw(user_raw_usage)

            for raw_line_item in user_raw_usage:
                if raw_line_item["plan_info"]["type"] == "stripe_metered":
                    unique_key = generate_unique_nyrkio_id(raw_line_item)
                    report_cpu_hours_consumed(
                        datetime.fromtimestamp(
                            raw_line_item["plan_info"]["unique_key"]["unique_time_slot"]
                        ),
                        raw_line_item["plan_info"]["stripe_customer_id"],
                        raw_line_item["consumption"]["nyrkio_cpu_hours"],
                        unique_key,
                    )

    if latest_usage_report:
        logger.info(
            f"We now imported s3 consumption reports up to and including {latest_usage_report}"
        )
        await store.set_latest_runner_report(latest_usage_report)

    return bool(raw_line_items)


async def loop_installations():
    store = DBStore()
    installations = await store.list_github_installations()
    statuses = []  # To return
    for inst in installations:
        installation_id = inst["installation"]["id"]
        # client_id = inst["installation"]["client_id"]
        app_access_token = await fetch_access_token(installation_id=installation_id)
        repo_list = await refresh_repo_list(app_access_token)
        # for repo in inst["repositories"]:
        for repo in repo_list["repositories"]:
            full_name = repo["full_name"]
            # repo_name = repo["name"]
            repo_owner = full_name.split("/")[0]
            queued_jobs = await check_queued_workflow_jobs(
                full_name, app_access_token=app_access_token
            )
            queued_jobs = filter_out_unsupported_jobs(queued_jobs)

            # Needed to prevent infinite loops in valid cases. If this is reached,
            # github will 403 because you reached the maximum requests allowed per hour.
            max_loops = 7
            while queued_jobs and max_loops > 0:
                max_loops -= 1
                logger.info(
                    f"Found {len(queued_jobs)} queued jobs for {full_name}. (poll from background worker)"
                )
                if len(queued_jobs) == 1:
                    logger.info(
                        "Will sleep a minute and check again if more runners are still needed."
                    )
                    await asyncio.sleep(60)
                    queued_jobs = await check_queued_workflow_jobs(full_name)
                    queued_jobs = filter_out_unsupported_jobs(queued_jobs)
                    if not queued_jobs:
                        break

                job = queued_jobs.pop()

                # Create a fakr workflow_job event, just like the ones github sends to the webhook
                fake_event = {
                    "action": "queued",
                    "workflow_job": job,
                    "repository": repo,
                    "sender": inst["sender"],
                    "installation": inst["installation"],
                }
                if repo_owner != inst["sender"]["login"]:
                    fake_event["organization"] = inst["installation"]["account"]
                logger.debug(fake_event)
                return_status = await workflow_job_event(fake_event)

                statuses.append(return_status)

                # Handling each job could take a few minutes.
                # So we need to refresh the queue to ensure we don't start too many runners in multile parallel threads/coroutines.
                if (
                    isinstance(return_status, dict)
                    and return_status.get("status") == "success"
                ):
                    queued_jobs = await check_queued_workflow_jobs(full_name)
                    queued_jobs = filter_out_unsupported_jobs(queued_jobs)
                elif return_status.get("status", "") == "nothing to do":
                    logger.info(
                        "Checked all installations for workflow jobs that could need runners. Nobody needed anything. (nothing to do)"
                    )
                elif (
                    return_status.get("status", "")
                    == "runner registration token denied"
                ):
                    logger.info(
                        f"Did not get a runner registration token from {repo_owner}. Continue to next user."
                    )
                    break
                else:
                    logger.error(return_status)
                    break

    return statuses


async def refresh_repo_list(app_access_token):
    url = "https://api.github.com/installation/repositories"
    client = httpx.AsyncClient()
    response = await client.get(
        url,
        headers={
            "Authorization": f"Bearer {app_access_token}",
            "Accept": "application/vnd.github+json",
            # "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            f"Couldn't get repo list for app_access_token {app_access_token[:11]}"
        )
        logger.error(response.json())


async def check_queued_workflow_jobs(repo_full_name, app_access_token=None):
    url = f"https://api.github.com/repos/{repo_full_name}/actions/runs?status=queued"
    client = httpx.AsyncClient()
    token = (
        app_access_token if app_access_token is not None else os.environ["GITHUB_TOKEN"]
    )
    response = await client.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            # "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if response.status_code <= 201:
        data = response.json()
        runs = data.get("workflow_runs", [])
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


def filter_out_unsupported_jobs(queued_jobs):
    supported_queue = []
    while queued_jobs:
        job = queued_jobs.pop()
        # Filter out those we're not gonna need anyway
        labels = job["labels"]
        supported = supported_instance_types()
        intersection = [lab for lab in labels if lab in supported]
        if intersection:
            supported_queue.append(job)
    return supported_queue


async def precompute_cached_change_points():
    """
    When new test results are POSTed (to /result/test_name_path) we immediately calculate and cache
    the change points for that test. However, the pre_computed change points can become invalidated
    for various reasons, for example if the user changes the algorithm parameters in UserSettings.
    When that happens, this function will find and recompute the change points.

    Thanks to this function, change points should almost always be ready and returned fast when a
    user is viewing a dashboard or otherwise issuing a GET.

    Also, the /results/test_name/summary end point may cause a re-compute of change points for all
    of your test result data, which can take minutes but more importantly will consume all memory
    and OOM. A goal of this background task is to compute the change points in smaller chunks so that
    won't happen.
    """
    print("precompute_cached_change_points")
    do_n_in_one_task = 150
    db = DBStore()
    all_users = await db.list_users()
    for user in all_users:
        user_id = user.id
        test_names = await db.get_test_names(user.id)
        for test_name in test_names:
            # print("precompute_cached_change_points: " +str(user.email) + " " + test_name)
            try:
                series, changes, is_cached = await _calc_changes(test_name, user_id)
            except Exception as exc:
                print(
                    f"Error in background task ({user.email} {test_name}) "
                    + str(type(exc))
                    + ": "
                    + str(exc)
                )
                continue

            if not is_cached:
                do_n_in_one_task -= 1
                print(
                    f"Computed new change points for user={user_id} ({user.email}), test_name={test_name}."
                )
                # We found a result series that didn't have cached change points and have now computed
                # the chánge points and cached them. We decrement the counter and once it reaches zero
                # it's time to exit and say goodbye.
                # We do this to split up the background computation into smaller chunks, to avoid hogging
                # the cpu for minutes at a time and to consume infinite amounts of memory when python
                # and numpy don't release the memory quickly enough.
                if do_n_in_one_task == 0:
                    return []

        await precompute_summaries_non_leaf(user.id)

    all_orgs = await db.list_orgs()
    for org_id in all_orgs:
        test_names = await db.get_test_names(org_id)
        for test_name in test_names:
            try:
                series, changes, is_cached = await _calc_changes(test_name, org_id)
            except Exception as exc:
                print(
                    f"Error in background task ({org_id} {test_name}) "
                    + str(type(exc))
                    + ": "
                    + str(exc)
                )
                continue

            if not is_cached:
                do_n_in_one_task -= 1
                print(
                    f"Computed new change points for org_id={org_id}, test_name={test_name}."
                )
                if do_n_in_one_task == 0:
                    return []

        await precompute_summaries_non_leaf(org_id)

    print("It appears as everything is cached and there's nothing more to do?")
    return []


async def precompute_summaries_non_leaf(user_or_org_id):
    print(
        "Once all leaf nodes are in the cache, go through each prefix and create a summary of its leaves   "
        + str(user_or_org_id)
    )

    store = DBStore()
    cache = await store.get_summaries_cache(user_or_org_id)
    leaves = get_leaves(cache.keys())
    test_name_prefix_todo = set(
        [("/".join(prefix.split("/")[:-1])) for prefix in leaves]
    )
    todo_next = set()

    while len(test_name_prefix_todo) > 0:
        summary = make_new_summary()

        # Get a prefix of the full test_names for which we just computed summaries
        test_name_prefix = set_pop(test_name_prefix_todo)
        test_name_parts = (
            test_name_prefix.split("/")
            if "/" in test_name_prefix
            else [test_name_prefix]
        )
        # Once we are done with this, we'll continue up the tree until we find the root of everything
        if isinstance(test_name_parts, list) and len(test_name_parts) > 1:
            todo_next.add("/".join(test_name_parts[:-1]))

        prefix_leaves = []
        for k in cache.keys():
            if k == "_id":
                continue
            if (
                # k.startswith(test_name_prefix)
                test_name_prefix in k
                and len(k) > len(test_name_prefix)
                and k[len(test_name_prefix)] == "/"
                and "/" not in k[len(test_name_prefix) + 1 :]
                and test_name_prefix != ""
            ):
                prefix_leaves.append(k)
        leaf_summaries = [cache[leaf] for leaf in prefix_leaves]
        for leaf_summary in leaf_summaries:
            summary["total_change_points"] = (
                summary["total_change_points"] + leaf_summary["total_change_points"]
            )
            if leaf_summary["newest_time"] is not None and (
                summary["newest_time"] is None
                or summary["newest_time"] < leaf_summary["newest_time"]
            ):
                summary["newest_time"] = leaf_summary["newest_time"]
                summary["newest_test_name"] = leaf_summary["newest_test_name"]
                summary["newest_change_point"] = leaf_summary["newest_change_point"]
            if leaf_summary["oldest_time"] is not None and (
                summary["oldest_time"] is None
                or summary["oldest_time"] > leaf_summary["oldest_time"]
            ):
                summary["oldest_time"] = leaf_summary["oldest_time"]
                summary["oldest_test_name"] = leaf_summary["oldest_test_name"]
                summary["oldest_change_point"] = leaf_summary["oldest_change_point"]
            if leaf_summary["largest_change"] is not None and (
                summary["largest_change"] is None
                or abs(summary["largest_change"]) < abs(leaf_summary["largest_change"])
            ):
                summary["largest_change"] = leaf_summary["largest_change"]
                summary["largest_test_name"] = leaf_summary["largest_test_name"]
                summary["largest_change_point"] = leaf_summary["largest_change_point"]

            cache[test_name_prefix] = summary

            if len(test_name_prefix_todo) == 0:
                test_name_prefix_todo = todo_next
                todo_next = set()

    await store.save_summaries_cache(user_or_org_id, cache)


async def precompute_summaries_leaves(test_name, changes, user_id):
    print("Pre-compute summary for " + str(user_id) + " " + test_name)
    store = DBStore()
    cache = await store.get_summaries_cache(user_id)
    summary = make_new_summary()
    for metric_name, analyzed_series in changes.items():
        for metric_name, cp_list in analyzed_series.change_points.items():
            for cp in cp_list:
                first = summary["total_change_points"] == 0
                if first or summary["newest_time"] < cp.time:
                    summary["newest_time"] = cp.time
                    summary["newest_test_name"] = test_name
                    summary["newest_change_point"] = cp.to_json()
                if first or summary["oldest_time"] > cp.time:
                    summary["oldest_time"] = cp.time
                    summary["oldest_test_name"] = test_name
                    summary["oldest_change_point"] = cp.to_json()
                if first or abs(summary["largest_change"]) < abs(
                    cp.forward_change_percent()
                ):
                    summary["largest_change"] = cp.forward_change_percent()
                    summary["largest_test_name"] = test_name
                    summary["largest_change_point"] = cp.to_json()

                summary["total_change_points"] += 1

        cache[test_name] = summary
    # print(cache)
    # TODO:The way this ended up, this could rather be done as a MongoDB update. This avoids a race
    # condition in the DB layer. Otoh if we only run this task in a single thread, nobody else is
    # writing to this record.
    # TODO: Should add a timestamp or done/todo switch to this document. Now we continuosly recompute
    # the non-leaf nodes even if nothing changed. For example, a simple model would be to flip the
    # value to "todo" whenever leaf summaries are updated, and "done" when non-leaf summaries are
    # written. In the same update, of course.
    await store.save_summaries_cache(user_id, cache)


def make_new_summary():
    return {
        "total_change_points": 0,
        "newest_time": None,
        "newest_test_name": None,
        "oldest_time": None,
        "oldest_test_name": None,
        "newest_change_point": None,
        "oldest_change_point": None,
        "largest_change": None,
        "largest_test_name": None,
    }


def set_pop(myset):
    for item in myset:
        myset.remove(item)
        return item


def is_leaf(check_node, all_nodes):
    for some_node in all_nodes:
        if check_node in some_node and check_node != some_node:
            return False
    return True


def get_leaves(all_nodes):
    leaves = []
    for some_node in all_nodes:
        if some_node == "_id":
            continue
        if is_leaf(some_node, all_nodes):
            leaves.append(some_node)
    return leaves
