# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
from typing import List

"""
This is a description of the core logic of Nyrkiö. It is written in such a way
that a performance engineer can understand it without having to read the code.
Though we use specific technologies internally (e.g. change point detection,
databases, etc), we try to avoid mentioning them here to keep the core logic
pure and free from technical details. This is all about the domain model.



Nyrkiö detects performance changes in test results.

Multiple performance test results (referred to as just "test results"
throughout the code) can be added together to form a test result series.

Test results must have a unique timestamp -- you cannot add a test result with
an existing timestamp to a series. However, you can update an existing test
result, for example when a performance engineer discovers that the
infrastructure they ran the test on is noisy, or they fix a bug in the test
code.

Test results can also be deleted.

Test results are made up of metrics and attributes. Metrics record some value
during a test run, e.g. the number of requests per second. Attributes provide
additional information about the test run, e.g. the version of the software or
the git commit hash.

A test result series must have a name. A test result series can be analyzed to
find changes in performance by identifying individual test results where some
metric changed in a statistically significant way from previous test results. A
performance change can represent either a regression or an improvement.

Notifications can be sent when a performance change is detected.

"""


class ResultMetric:
    def __init__(self, name, unit, value):
        self.name = name
        self.unit = unit
        self.value = value


class PerformanceTestResult:
    def __init__(self, timestamp, metrics: List[ResultMetric], attributes):
        self.timestamp = timestamp
        self.metrics = metrics
        self.attributes = attributes


class PerformanceTestResultSeries:
    def __init__(self, name):
        self.results = []
        self.name = name

    def add_result(self, result: PerformanceTestResult):
        if result in self.results:
            raise PerformanceTestResultExistsError()

        self.results.append(result)

    def delete_result(self, timestamp):
        """
        Delete a result from the series

        If the result does not exist, do nothing.
        """
        self.results = [r for r in self.results if r.timestamp != timestamp]

    def calculate_changes(self):
        from ..hunter.hunter.series import Series

        timestamps = [r.timestamp for r in self.results]

        metric_units = {}
        for r in self.results:
            for m in r.metrics:
                metric_units[m.name] = m.unit

        metric_data = defaultdict(list)
        for r in self.results:
            for m in r.metrics:
                metric_data[m.name].append(m.value)

        attributes = defaultdict(list)
        for r in self.results:
            for k, v in r.attributes.items():
                attributes[k].append(v)

        series = Series(
            self.name, None, timestamps, metric_units, metric_data, attributes
        )
        return series.analyze().change_points


class PerformanceTestResultExistsError(Exception):
    pass
