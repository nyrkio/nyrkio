import logging
from typing import Dict

from hunter.series import AnalyzedSeries

from backend.core.core import (
    PerformanceTestResult,
    PerformanceTestResultSeries,
    ResultMetric,
)
from backend.core.config import Config
from backend.db.db import DBStore, NULL_DATETIME


async def cache_changes(
    cp: Dict[str, AnalyzedSeries], user_id, series: PerformanceTestResultSeries
):
    store = DBStore()
    await store.persist_change_points(cp, user_id, series.get_series_id())
    # The summary data could in fact naturally be part of AnalyzedSeries, but it started as
    # a side project and so its data is too.
    await precompute_summaries_leaves(series.name, cp, user_id)


async def get_cached_or_calc_changes(user_id, series):
    if user_id is None:
        # Dummy user just because the caching code was written such that it assumes a user
        user_id = '000000000000000000000000'

    store = DBStore()
    cached_cp = await store.get_cached_change_points(user_id, series.get_series_id())
    if cached_cp is not None and len(cached_cp) > 0 and series.results:
        # Metrics may have been disabled or enabled after they were cached.
        # If so, invalidate the entire result and start over.
        series_metric_names = set([m.name for m in series.results[0].metrics])
        cached_metric_names = set([o for o in cached_cp])

        cp = {}
        if series_metric_names == cached_metric_names:
            for metric_name, analyzed_json in cached_cp.items():
                cp[metric_name] = AnalyzedSeries.from_json(analyzed_json)

            return cp, True

    if cached_cp is not None and len(cached_cp) == 0:
        # We computed the change points, and there were zero of them
        return cached_cp, True

    # "else"
    # Cached change points not found or have expired, (re)compute from start:
    changes = series.calculate_change_points()
    await cache_changes(changes, user_id, series)
    return changes, False


def _build_result_series(
    test_name, results, results_meta, disabled=None, core_config=None
):
    series = PerformanceTestResultSeries(test_name, core_config)

    metadata_missing = not all(results_meta)
    if metadata_missing:
        # Find any empty dicts and replace them with a NULL_DATETIME. This
        # happens when test results have no metadata, which is the case for
        # old data.
        for i, d in enumerate(results_meta):
            if not d:
                results_meta[i] = {"last_modified": NULL_DATETIME}

    results_with_meta = list(zip(results, results_meta))

    # TODO(matt) - iterating like this is silly, we should just be able to pass
    # the results in batch.
    # Henrik: I'm pretty sure there exists a Mongodb aggregation query that would do this while
    # fetching the data. Using $lookup and $push.
    for r, meta in results_with_meta:
        metrics = []

        if "metrics" not in r:
            logging.error(f"Missing metrics in result: {r}")

        for m in r["metrics"]:
            # Metrics can opt out of change detection
            if disabled and m["name"] in disabled:
                continue

            rm = ResultMetric(name=m["name"], unit=m["unit"], value=m["value"])
            metrics.append(rm)

        result = PerformanceTestResult(
            timestamp=r["timestamp"],
            metrics=metrics,
            attributes=r["attributes"],
            last_modified=meta["last_modified"],
        )
        series.add_result(result)

    return series


async def _calc_changes(
    test_name, user_id=None, notifiers=None, pull_request=None, pr_commit=None
):
    store = DBStore()
    series = None

    if user_id is None:
        results, results_meta = await store.get_default_data(test_name)
        series = _build_result_series(test_name, results, results_meta)
    else:
        results, results_meta = await store.get_results(
            user_id, test_name, pull_request, pr_commit
        )
        disabled = await store.get_disabled_metrics(user_id, test_name)
        core_config = await _get_user_config(user_id)
        series = _build_result_series(
            test_name, results, results_meta, disabled, core_config
        )
    changes, is_cached = await get_cached_or_calc_changes(user_id, series)
    return series, changes, is_cached


async def calc_changes(
    test_name, user_id=None, notifiers=None, pull_request=None, pr_commit=None
):
    series, changes, is_cached = await _calc_changes(
        test_name, user_id, notifiers, pull_request, pr_commit
    )
    reports = await series.produce_reports(changes, notifiers)
    return reports


async def _get_user_config(user_id):
    store = DBStore()
    config, _ = await store.get_user_config(user_id)
    core_config = config.get("core", None)
    if core_config:
        core_config = Config(**core_config)
    return core_config


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
