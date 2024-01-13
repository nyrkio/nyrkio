# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
import json
from typing import List
import httpx
import logging

from hunter.report import Report, ReportType
from hunter.series import Series

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

    async def calculate_changes(self):
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

        change_points = series.analyze().change_points_by_time
        report = GitHubReport(series, change_points)
        produced_report = await report.produce_report(self.name, ReportType.JSON)
        return json.loads(produced_report)


class PerformanceTestResultExistsError(Exception):
    pass


class GitHubReport(Report):
    def __init__(self, series: Series, change_points: List):
        super().__init__(series, change_points)

    @staticmethod
    async def add_github_commit_msg(attributes):
        """
        Annotate attributes with GitHub commit messages.

        If attributes contains a 'git_commit' key and the 'git_repo' indicates a
        GitHub repository, add a 'commit_msg' key with the first line of the commit
        message.
        """
        if "git_commit" not in attributes:
            return

        # TODO(mfleming): Handle multiple git repos
        attr_repo = attributes["git_repo"][0]
        gh_url = "https://github.com"
        if not attr_repo.startswith(gh_url):
            return

        async with httpx.AsyncClient() as client:
            repo = attr_repo[len(gh_url) + 1 :]
            commit = attributes["git_commit"][0]
            response = await client.get(
                f"https://api.github.com/repos/{repo}/commits/{commit}"
            )
            if response.status_code == 200:
                # Only save the first line of the message
                commit_msg = response.json()["commit"]["message"].split("\n")[0]
                attributes["commit_msg"] = [commit_msg]
                logging.error(
                    "Adding commit message {} to {}".format(commit_msg, commit)
                )
            else:
                logging.error(
                    f"Failed to fetch commit message for {repo}/{commit}: {response.status_code}"
                )

    async def produce_report(self, test_name: str, report_type: ReportType):
        change_points = self._Report__change_points
        logging.error(change_points)
        for cp in change_points:
            await GitHubReport.add_github_commit_msg(cp.attributes)

        report = super().produce_report(test_name, report_type)
        return report
