import asyncio

from backend.core.core import (
    PerformanceTestResult,
    PerformanceTestResultSeries,
    PerformanceTestResultExistsError,
    ResultMetric,
)

from backend.core.core import GitHubReport

import pytest


def test_add_result():
    """Add a performance test result to a series"""
    series = PerformanceTestResultSeries("benchmark1")

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))


def test_adding_existing_result_fails():
    """Adding an existing result fails"""
    series = PerformanceTestResultSeries("benchmark1")

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}
    result = PerformanceTestResult(1, metrics, attr)

    series.add_result(result)
    with pytest.raises(PerformanceTestResultExistsError):
        series.add_result(result)


@pytest.mark.anyio
async def test_calculate_changes_in_series():
    """Calculate changes in a series"""
    series = PerformanceTestResultSeries("benchmark1")

    attr = {"attr1": "value1", "attr2": "value2"}
    metrics = [ResultMetric("metric1", "µs", 1.0)]

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))

    # Identical metrics should not result in any changes
    changes = await series.calculate_changes()
    assert "benchmark1" in changes
    assert "metric1" not in changes["benchmark1"]

    # Create a new series with a change in metric1
    series = PerformanceTestResultSeries("benchmark2")
    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    metrics = [ResultMetric("metric1", "µs", 2.0)]
    series.add_result(PerformanceTestResult(3, metrics, attr))

    changes = await series.calculate_changes()
    assert "benchmark2" in changes
    for ch in changes["benchmark2"][0]["changes"]:
        assert ch["metric"] == "metric1"


def test_deleting_result_from_series():
    """Delete a result from a series"""
    series = PerformanceTestResultSeries("benchmark1")

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))

    series.delete_result(2)

    assert len(series.results) == 2
    assert series.results[0].timestamp == 1
    assert series.results[1].timestamp == 3


def test_deleting_non_existing_result_from_series():
    """Delete a non-existing result from a series"""
    series = PerformanceTestResultSeries("benchmark1")

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.delete_result(4)

    assert len(series.results) == 1
    assert series.results[0].timestamp == 1

    empty_series = PerformanceTestResultSeries("benchmark2")
    empty_series.delete_result(1)
    assert len(empty_series.results) == 0


@pytest.mark.anyio
async def test_calculate_changes_with_multiple_metrics():
    """Calculate changes in a series with multiple metrics"""
    testname = "benchmark1"
    series = PerformanceTestResultSeries(testname)

    attr = {"attr1": "value1", "attr2": "value2"}
    metrics = [ResultMetric("metric1", "µs", 1.0), ResultMetric("metric2", "µs", 1.0)]

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))

    # Identical metrics should not result in any changes
    changes = await series.calculate_changes()
    assert testname in changes
    assert "metric1" not in changes[testname]
    assert "metric2" not in changes[testname]

    # Create a new series with a change in metric1 and metric2
    testname = "benchmark2"
    series = PerformanceTestResultSeries(testname)
    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    metrics = [ResultMetric("metric1", "µs", 2.0), ResultMetric("metric2", "µs", 2.0)]
    series.add_result(PerformanceTestResult(3, metrics, attr))

    changes = await series.calculate_changes()
    assert testname in changes
    for ch in changes[testname][0]["changes"]:
        assert ch["metric"] in ["metric1", "metric2"]


@pytest.mark.anyio
async def test_github_message(client):
    """Test github message"""
    attr = {
        "git_repo": ["https://github.com/torvalds/linux"],
        "git_commit": ["0dd3ee31125508cd67f7e7172247f05b7fd1753a"],
        "branch": ["master"],
    }
    await GitHubReport.add_github_commit_msg(attr)
    assert attr["commit_msg"] == ["Linux 6.7"]


def test_tigerbeetle_data(shared_datadir):
    """Test tigerbeetle data"""
    series = PerformanceTestResultSeries("tigerbeetle")

    json_data = None
    path = (shared_datadir / "tigerbeetle.json").resolve()
    with open(path) as f:
        import json

        json_data = json.load(f)

    for result in json_data:
        metrics = []
        for m in result["metrics"]:
            # Only focus on load_accepted metrics to make the test simpler
            if m["name"] == "load_accepted":
                metrics.append(ResultMetric(m["name"], m["unit"], m["value"]))

        series.add_result(
            PerformanceTestResult(result["timestamp"], metrics, result["attributes"])
        )

    changes = asyncio.run(series.calculate_changes())

    assert len(changes) == 1
    assert "tigerbeetle" in changes
    assert len(changes["tigerbeetle"]) == 2

    expected_commits = (
        "e88458cb2faf40d97df0f3b5feea66c494063f4c",
        "7a724369d85c378b9eb311cb41853cef58ecc07e",
    )
    for change in changes["tigerbeetle"]:
        assert change["attributes"]["git_commit"][0] in expected_commits
        expected_commits = expected_commits[1:]


def test_add_results_in_any_order_returns_sorted():
    """Test that adding results in any order returns sorted results"""
    series = PerformanceTestResultSeries("benchmark1")

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(3, metrics, attr))
    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))

    assert series.results[0].timestamp == 1
    assert series.results[1].timestamp == 2
    assert series.results[2].timestamp == 3
