from backend.main import PerformanceTestResult, PerformanceTestResultSeries, PerformanceTestResultExistsError

import pytest

def test_add_result():
    """Add a performance test result to a series"""
    series = PerformanceTestResultSeries()

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))

def test_adding_existing_result_fails():
    """Adding an existing result fails"""
    series = PerformanceTestResultSeries()

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}
    result = PerformanceTestResult(1, metrics, attr)

    series.add_result(result)
    with pytest.raises(PerformanceTestResultExistsError):
        series.add_result(result)

def test_calculate_changes_in_series():
    """Calculate changes in a series"""
    series = PerformanceTestResultSeries()

    metrics = {"metric1": 1.0, "metric2": 2.0}
    attr = {"attr1": "value1", "attr2": "value2"}

    series.add_result(PerformanceTestResult(1, metrics, attr))
    series.add_result(PerformanceTestResult(2, metrics, attr))
    series.add_result(PerformanceTestResult(3, metrics, attr))

    # Identical metrics should not result in any changes
    changes = series.calculate_changes()

    assert len(changes) == 0

    # Create a new series with a change in metric1
    series = PerformanceTestResultSeries()
    metrics = [{"metric1": 1.0, "metric2": 2.0}, {"metric1": 2.0, "metric2": 2.0}]
    series.add_result(PerformanceTestResult(1, metrics[0], attr))
    series.add_result(PerformanceTestResult(2, metrics[1], attr))
    changes = series.calculate_changes()
    assert len(changes) == 1