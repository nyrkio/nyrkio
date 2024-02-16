# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
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

        options = AnalysisOptions()
        options.min_magnitude = self.config.min_magnitude
        options.max_pvalue = self.config.max_pvalue

        change_points = series.analyze(options).change_points_by_time
        report = GitHubReport(series, change_points)
        produced_report = await report.produce_report(self.name, ReportType.JSON)
        return json.loads(produced_report)


class PerformanceTestResultExistsError(Exception):
    pass


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
            logging.error(f"GitHub API rate limit exceeded: {used}/{limit} reqs used")

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
        """
        if "git_commit" not in attributes:
            return

        # TODO(mfleming): Handle multiple git repos
        attr_repo = attributes["git_repo"][0]
        gh_url = "https://github.com"
        if not attr_repo.startswith(gh_url):
            return

        repo = attr_repo[len(gh_url) + 1 :]
        commit = attributes["git_commit"][0]

        msg = await cached_get(repo, commit)
        if msg:
            attributes["commit_msg"] = [msg]

    async def produce_report(self, test_name: str, report_type: ReportType):
        change_points = self._Report__change_points
        for cp in change_points:
            await GitHubReport.add_github_commit_msg(cp.attributes)

        report = super().produce_report(test_name, report_type)
        return report
