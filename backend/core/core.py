# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
from datetime import datetime
import json
from typing import List
import httpx
import logging
from sortedcontainers import SortedList

from hunter.report import Report, ReportType
from hunter.series import Series, AnalysisOptions

from backend.core.sieve import sieve_cache
from backend.core.config import Config

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
    def __init__(self, name, config=None):
        self.results = SortedList(key=lambda r: r.timestamp)
        self.name = name

        if not config:
            config = Config()

        self.config = config

    def add_result(self, result: PerformanceTestResult):
        """
        Add a test result to the series.

        Results can be added in any order and will be stored internally
        sorted by timestamp.

        Adding results with the same timestamp is not allowed.
        """
        if result in self.results:
            raise PerformanceTestResultExistsError()

        self.results.add(result)

    def delete_result(self, timestamp):
        """
        Delete a result from the series

        If the result does not exist, do nothing.
        """
        self.results = [r for r in self.results if r.timestamp != timestamp]

    class SingleMetricSeries:
        def __init__(self):
            self.timestamps = []
            self.attributes = defaultdict(list)
            self.metric_unit = None
            self.metric_data = []

        def add_result(self, timestamp, metric, attributes):
            self.timestamps.append(timestamp)
            self.metric_unit = metric.unit
            self.metric_data.append(metric.value)
            for k, v in attributes.items():
                self.attributes[k].append(v)

    async def calculate_changes(self, notifiers=None):
        # TODO(mfleming) Instead of building this dict here we should refactor
        # PerformanceTestResultSeries to store the data in this way, i.e. by
        # metric name, when we add results.
        data = {}
        for r in self.results:
            for m in r.metrics:
                if m.name not in data:
                    s = data[m.name] = PerformanceTestResultSeries.SingleMetricSeries()
                else:
                    s = data[m.name]

                s.add_result(r.timestamp, m, r.attributes)

        # Hunter has the ability to analyze multiple series at once but requires
        # that all series have the same number of data points (timestamps,
        # metric values, etc).  This isn't always true for us, for example when
        # a user only recently started collecting data for a new metric. So we
        # analyze each series separately.
        reports = []
        for name, m in data.items():
            timestamps = m.timestamps
            metric_units = {name: m.metric_unit}
            metric_data = {name: m.metric_data}
            attributes = m.attributes
            logging.error(f"{timestamps}, {metric_units}, {metric_data}, {attributes}")
            series = Series(
                self.name, None, timestamps, metric_units, metric_data, attributes
            )

            options = AnalysisOptions()
            options.min_magnitude = self.config.min_magnitude
            options.max_pvalue = self.config.max_pvalue

            analyzed_series = series.analyze(options)
            change_points = analyzed_series.change_points_by_time
            report = GitHubReport(m, change_points)
            produced_report = await report.produce_report(self.name, ReportType.JSON)
            reports.append(json.loads(produced_report))

            if notifiers:
                for notifier in notifiers:
                    await notifier.notify({self.name: analyzed_series})

        # Merge all change points into a single list
        final_report = {}
        for report in reports:
            changes = report[self.name]

            if not final_report:
                final_report[self.name] = changes
                continue

            timestamps = [c["time"] for c in changes]
            change_points = [c["changes"] for c in changes]
            existing_timestamps = [c["time"] for c in final_report[self.name]]

            for t in timestamps:
                if t not in existing_timestamps:
                    final_report[self.name].extend(changes)
                else:
                    index = existing_timestamps.index(t)
                    existing_cp = final_report[self.name][index]
                    for c in change_points:
                        existing_cp["changes"].extend(c)

        return final_report


class PerformanceTestResultExistsError(Exception):
    pass


class GitHubRateLimitExceededError(Exception):
    def __init__(self, used, limit, reset):
        self.used = used
        self.limit = limit
        self.reset = reset

    def __str__(self):
        timestamp = datetime.fromtimestamp(int(self.reset))
        return f"GitHub API rate limit exceeded: {self.used}/{self.limit} reqs used. Resets at {timestamp}"


# The assumption is that the first line of a commit message is typically 80
# characters or less. So storing 16K entries means this cache will use about
# 1.2MiB of memory. This is an important cache.
CACHE_SIZE = 16 * 1024


@sieve_cache(maxsize=CACHE_SIZE)
async def cached_get(repo, commit):
    """
    Fetch the commit message for a GitHub commit if it hasn't been fetched
    before and save the first line of the commit message in the cache.

    On cache miss, if the HTTP request fails then nothing is added to the cache.

    If we exceed the GitHub API rate limit, raise a GitHubRateLimitExceededError.
    """
    commit_msg = None
    client = httpx.AsyncClient()
    response = await client.get(f"https://api.github.com/repos/{repo}/commits/{commit}")
    if response.status_code == 200:
        # Only save the first line of the message
        commit_msg = response.json()["commit"]["message"].split("\n")[0]
        logging.debug("Adding commit message {} to {}".format(commit_msg, commit))
    else:
        logging.error(
            f"Failed to fetch commit message for {repo}/{commit}: {response.status_code}"
        )

        # Check x-ratelimit-used and x-ratelimit-remaining headers
        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining and int(remaining) <= 0:
            used = response.headers.get("x-ratelimit-used")
            limit = response.headers.get("x-ratelimit-limit")
            reset = response.headers.get("x-ratelimit-reset")
            raise GitHubRateLimitExceededError(used, limit, reset)

    return commit_msg


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

        Raises GitHubRateLimitExceededError if the GitHub API rate limit is exceeded.
        """
        if "git_commit" not in attributes:
            return

        attr_repo = attributes["git_repo"]
        gh_url = "https://github.com"
        if not attr_repo.startswith(gh_url):
            return

        repo = attr_repo[len(gh_url) + 1 :]
        commit = attributes["git_commit"]

        msg = await cached_get(repo, commit)
        if msg:
            attributes["commit_msg"] = msg

    async def produce_report(self, test_name: str, report_type: ReportType):
        change_points = self._Report__change_points
        for cp in change_points:
            try:
                await GitHubReport.add_github_commit_msg(cp.attributes)
            except GitHubRateLimitExceededError as e:
                logging.error(e)

        report = super().produce_report(test_name, report_type)
        return report
