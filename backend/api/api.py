# Copyright (c) 2024, Nyrkiö Oy

from typing import Dict, List, Union
from datetime import datetime

from backend.core.core import (
    PerformanceTestResult,
    PerformanceTestResultSeries,
    ResultMetric,
)
from backend.core.config import Config

from fastapi import FastAPI, APIRouter, Depends, HTTPException

from backend.auth import auth
from backend.api.admin import admin_router
from backend.api.billing import billing_router
from backend.api.config import config_router
from backend.api.model import TestResults
from backend.api.organization import org_router
from backend.api.public import public_router
from backend.api.user import user_router
from backend.db.db import DBStoreMissingRequiredKeys, DBStoreResultExists, User, DBStore
from backend.notifiers.slack import SlackNotifier

from hunter.series import AnalyzedSeries

app = FastAPI(openapi_url="/openapi.json")


api_router = APIRouter()


@api_router.post("/result/{test_name:path}/changes/enable")
async def enable_changes(
    test_name: str,
    user: User = Depends(auth.current_active_user),
    metrics: List[str] = [],
):
    store = DBStore()
    await store.enable_changes(user.id, test_name, metrics)
    return {}


@api_router.post("/result/{test_name:path}/changes/disable")
async def disable_changes(
    test_name: str,
    user: User = Depends(auth.current_active_user),
    metrics: List[str] = [],
):
    if not metrics:
        raise HTTPException(
            status_code=400, detail="No metrics to disable change detection for"
        )
    store = DBStore()
    await store.disable_changes(user.id, test_name, metrics)
    return {}


@api_router.get("/result/{test_name:path}/changes")
async def changes(
    test_name: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    results = await store.get_results(user.id, test_name)
    disabled = await store.get_disabled_metrics(user.id, test_name)
    core_config = await _get_user_config(user.id)
    config = await store.get_user_config(user.id)
    notifiers = await _get_notifiers(notify, config, user)
    return await calc_changes(
        test_name, results, disabled, core_config, notifiers, user
    )


# @api_router.get("/result/{test_name_prefix:path}/summary")
# async def get_subtree_summary(
#     test_name_prefix: str, user: User = Depends(auth.current_active_user)
# ) -> Dict:
#     """
#     Get all change points for all test results that are in the sub-tree of `test_name_prefix` and
#     return a summary of that data.
#
#     The UI would use this information to show something like "project: 57 change points, the latest
#     on 2024-04-20".
#
#     Note that for this feature we have added pre-computation and storage of change points.
#     Without such pre-compute, we would here constantly be re-computing all test results of the user!
#     """
#     subtree_test_names = await store.get_test_names(user.id, test_name_prefix)
#
#     if not subtree_test_names:
#         raise HTTPException(status_code=404, detail="Not Found")
#
#     core_config = await _get_user_config(user.id)
#
#     for test_name in subtree_test_names:
#         change_points = await calc_changes(test_name, results, core_config=core_config)
#         subtree_changes[test_name] = change_points


@api_router.get("/results")
async def results(user: User = Depends(auth.current_active_user)) -> List[Dict]:
    store = DBStore()
    results = await store.get_test_names(user.id)
    return [{"test_name": name} for name in results]


@api_router.delete("/results")
async def delete_results(user: User = Depends(auth.current_active_user)) -> List:
    store = DBStore()
    await store.delete_all_results(user)
    return []


def _strip_last_modified(results):
    for r in results:
        if "last_modified" in r:
            del r["last_modified"]
    return results


@api_router.get("/result/{test_name:path}")
async def get_result(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> List[Dict]:
    store = DBStore()
    test_names = await store.get_test_names(user.id)

    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    return _strip_last_modified(await store.get_results(user.id, test_name))


@api_router.delete("/result/{test_name:path}")
async def delete_result(
    test_name: str,
    timestamp: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
) -> List[Dict]:
    store = DBStore()
    test_names = await store.get_test_names(user.id)

    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    await store.delete_result(user.id, test_name, timestamp)
    return []


@api_router.post("/result/{test_name:path}")
async def add_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    store = DBStore()
    try:
        await store.add_results(user.id, test_name, data.root)
    except DBStoreResultExists as e:
        explanation = {
            "reason": "Result already exists for key",
            "data": e.key,
        }
        raise HTTPException(status_code=400, detail=explanation)
    except DBStoreMissingRequiredKeys as e:
        explanation = {
            "reason": "Result is missing required keys",
            "data": e.missing_keys,
        }
        raise HTTPException(status_code=400, detail=explanation)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid data")

    # Compute the change points and persist the result so they are cheap to GET later.
    # Since we compute them after POSTing them, may as well return the results to the user.
    return await changes(test_name, notify=1, user=user)
    # return {}


async def cache_changes(
    changes: Dict[str, AnalyzedSeries], user: User, series: PerformanceTestResultSeries
):
    store = DBStore()
    await store.persist_change_points(changes, user.id, series.get_series_id())


async def get_cached_or_calc_changes(user: User, series: PerformanceTestResultSeries):
    if user is None:
        # We only cache change points for logged in users
        return series.calculate_change_points()

    store = DBStore()
    cached_cp = await store.get_change_points(user.id, series.get_series_id())
    changes = {}
    if cached_cp is not None:
        for metric_name, analyzed_json in cached_cp["change_points"].items():
            changes[metric_name] = AnalyzedSeries.from_json(analyzed_json)

    else:
        changes = series.calculate_change_points()
        await cache_changes(changes, user, series)
    return changes


def _build_result_series(test_name, results, disabled=None, core_config=None):
    series = PerformanceTestResultSeries(test_name, core_config)

    # TODO(matt) - iterating like this is silly, we should just be able to pass
    # the results in batch.
    last_mod_timestamps = [datetime(1970, 1, 1, 0, 0, 0, 0)]
    for r in results:
        metrics = []
        for m in r["metrics"]:
            # Metrics can opt out of change detection
            if disabled and m["name"] in disabled:
                continue

            rm = ResultMetric(name=m["name"], unit=m["unit"], value=m["value"])
            metrics.append(rm)
            last_mod_timestamps.append(r["last_modified"])

        result = PerformanceTestResult(
            timestamp=r["timestamp"], metrics=metrics, attributes=r["attributes"]
        )
        series.add_result(result)

    series.touch(max(last_mod_timestamps))
    return series


async def calc_changes(
    test_name, results, disabled=None, core_config=None, notifiers=None, user=None
):
    series = _build_result_series(test_name, results, disabled, core_config)
    changes = await get_cached_or_calc_changes(user, series)
    reports = await series.produce_reports(changes, notifiers)
    return reports


@api_router.get("/default/results")
async def default_results() -> List[str]:
    store = DBStore()
    return await store.get_default_test_names()


@api_router.get("/default/result/{test_name}")
async def default_result(test_name: str) -> List[Dict]:
    store = DBStore()
    return await store.get_default_data(test_name)


@api_router.get("/default/result/{test_name}/changes")
async def default_changes(test_name: str):
    store = DBStore()
    results = await store.get_default_data(test_name)
    return await calc_changes(test_name, results)


# Must come at the end, once we've setup all the routes
app.include_router(api_router, prefix="/api/v0")
app.include_router(auth.auth_router, prefix="/api/v0")
app.include_router(user_router, prefix="/api/v0")
app.include_router(admin_router, prefix="/api/v0")
app.include_router(config_router, prefix="/api/v0")
app.include_router(public_router, prefix="/api/v0")
app.include_router(org_router, prefix="/api/v0")
app.include_router(billing_router, prefix="/api/v0")


@app.on_event("startup")
async def do_db():
    from backend.db.db import do_on_startup

    await do_on_startup()


async def _get_notifiers(notify: Union[int, None], config: dict, user: User) -> list:
    notifiers = []
    if notify:
        slack = config.get("slack", {})
        if slack and slack.get("channel"):
            if not user.slack:
                raise HTTPException(status_code=400, detail="Slack not configured")

            url = user.slack["incoming_webhook"]["url"]
            channel = slack["channel"]
            notifiers.append(SlackNotifier(url, [channel]))
    return notifiers


async def _get_user_config(user_id: str):
    store = DBStore()
    config = await store.get_user_config(user_id)
    core_config = config.get("core", None)
    if core_config:
        core_config = Config(**core_config)
    return core_config
