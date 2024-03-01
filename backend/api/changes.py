from fastapi import HTTPException

from backend.core.core import (
    PerformanceTestResult,
    PerformanceTestResultSeries,
    ResultMetric,
    Config,
)

from backend.notifiers.slack import SlackNotifier


async def calc_changes(
    test_name, results, disabled=None, core_config=None, notifiers=None
):
    series = PerformanceTestResultSeries(test_name, core_config)

    # TODO(matt) - iterating like this is silly, we should just be able to pass
    # the results in batch.
    for r in results:
        metrics = []
        for m in r["metrics"]:
            # Metrics can opt out of change detection
            if disabled and m["name"] in disabled:
                continue

            rm = ResultMetric(name=m["name"], unit=m["unit"], value=m["value"])
            metrics.append(rm)

        result = PerformanceTestResult(
            timestamp=r["timestamp"], metrics=metrics, attributes=r["attributes"]
        )
        series.add_result(result)

    return await series.calculate_changes(notifiers)