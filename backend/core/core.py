# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from typing import List, Dict
import httpx
import logging
from sortedcontainers import SortedList

from hunter.report import Report, ReportType
from hunter.series import Series, AnalysisOptions, AnalyzedSeries

from backend.core.sieve import sieve_cache
from backend.core.config import Config
from backend.db.db import NULL_DATETIME

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
    def __init__(
        self, timestamp, metrics: List[ResultMetric], attributes, last_modified=None
    ):
        self.timestamp = timestamp
        self.metrics = metrics
        self.attributes = attributes

        if last_modified is None:
            last_modified = datetime.now(tz=timezone.utc)
        if not isinstance(last_modified, datetime):
            raise ValueError("last_modified must be of type datetime.")
        self._last_modified = last_modified


class PerformanceTestResultSeries:
    def __init__(self, name, config=None, change_points_timestamp=None):
        self.results = SortedList(key=lambda r: r.timestamp)
        self.name = name
        # If we know the timestamp of cached change points, then we can keep track of whether and
        # how many points in our tail end are new = newer than the cached change points.
        self.change_points_timestamp = change_points_timestamp

        if not config:
            config = Config()

        self.config = config

    def last_modified(self):
        if not self.results:
            return NULL_DATETIME

        return max([result._last_modified for result in self.results])

    def get_series_id(self):
        """
        Return an id that can be used to compare this series to others.

        In particular, we want to assert with reasonable certainty whether some cached change points
        are valid for this series, or whether we need to invalidate cache and re-compute cp's for
        this series.
        """
        return (
            self.name,
            self.config.max_pvalue,
            self.config.min_magnitude,
            self.last_modified(),
        )

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

    def tail_newer_than_cache(self):
        if self.change_points_timestamp is None or not self.change_points_timestamp:
            return 0

        newer_than_cache = 0
        for r in self.results:
            if self.change_points_timestamp < r._last_modified:
                newer_than_cache += 1
            else:
                # We only care about the case where newer data points have been appended to the tail
                # end of the series.
                if newer_than_cache > 0:
                    return 0

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

        def add_result(self, timestamp, result_metric, attributes):
            self.timestamps.append(timestamp)
            self.metric_unit = result_metric.unit
            self.metric_name = result_metric.name
            self.metric_data.append(result_metric.value)
            for k, v in attributes.items():
                self.attributes[k].append(v)

        def __iter__(self):
            for i in range(len(self.timestamps)):
                t = self.timestamps[i]
                d = self.data[i]
                obj = {
                    "timestamp": t,
                    "metric_name": self.metric_name,
                    "metric_unit": self.metric_unit,
                    "metric_data": d,
                    "attributes": {},
                }
                for k, v in self.attributes.items():
                    obj["attributes"][k] = v[i]
                yield obj

    # def per_metric_series(self) -> Dict[str, SingleMetricSeries]:
    #     # TODO(mfleming) Instead of building this dict here we should refactor
    #     # PerformanceTestResultSeries to store the data in this way, i.e. by
    #     # metric name, when we add results.
    #     data = {}
    #     for r in self.results:
    #         for rm in r.metrics:
    #             if rm.name not in data:
    #                 s = data[rm.name] = PerformanceTestResultSeries.SingleMetricSeries()
    #             else:
    #                 s = data[rm.name]
    #
    #             s.add_result(r.timestamp, rm, r.attributes)
    #
    #     return data

    def per_metric_series(self, split_new=False) -> Dict[str, SingleMetricSeries]:
        old_data = {}
        new_data = {}
        for r in self.results:
            data = old_data
            if split_new:
                if self.change_points_timestamp < r._last_modified:
                    data = new_data
                else:
                    if new_data:
                        raise ValueError(
                            "Cannot split series cleanly at {}. Please do a full recompute of change points and use split_new=True".format(
                                self.change_points_timestamp
                            )
                        )

            for rm in r.metrics:
                if rm.name not in data:
                    s = data[rm.name] = PerformanceTestResultSeries.SingleMetricSeries()
                else:
                    s = data[rm.name]

                s.add_result(r.timestamp, rm, r.attributes)

        if split_new:
            return old_data, new_data
        else:
            return old_data

    async def calculate_changes(self, notifiers=None):
        change_points = self.calculate_change_points()
        reports = await self.produce_reports(change_points, notifiers)
        return reports

    def calculate_change_points(self) -> Dict[str, AnalyzedSeries]:
        data = self.per_metric_series()
        # Hunter has the ability to analyze multiple series at once but requires
        # that all series have the same number of data points (timestamps,
        # metric values, etc).  This isn't always true for us, for example when
        # a user only recently started collecting data for a new metric. So we
        # analyze each series separately.
        all_change_points = {}
        for metric_name, m in data.items():
            metric_timestamps = m.timestamps
            metric_units = {metric_name: m.metric_unit}
            metric_data = {metric_name: m.metric_data}
            attributes = m.attributes
            series = Series(
                self.name,
                None,
                metric_timestamps,
                metric_units,
                metric_data,
                attributes,
            )

            options = AnalysisOptions()
            options.min_magnitude = self.config.min_magnitude
            options.max_pvalue = self.config.max_pvalue

            analyzed_series = series.analyze(options)
            all_change_points[metric_name] = analyzed_series

        return all_change_points

    def incremental_change_points(self, old_cp) -> Dict[str, AnalyzedSeries]:
        all_change_points = {}
        data, new_data = self.per_metric_series(split_new=True)
        if not _validate_cached_series(self.name, data, old_cp):
            logging.warning(
                "{}: Discarding cached change points and doing a full compute.".format(
                    self.name
                )
            )
            return self.calculate_change_points()

        options = AnalysisOptions()
        options.min_magnitude = self.config.min_magnitude
        options.max_pvalue = self.config.max_pvalue

        for metric_name, new_results in new_data.items():
            analyzed_series = old_cp[metric_name]
            for new_result in new_results:
                analyzed_series.append(
                    new_result["timestamp"],
                    {metric_name: new_result["metric_data"]},
                    new_result["attributes"],
                )
            all_change_points[metric_name] = analyzed_series

        return all_change_points

    async def produce_reports(
        self, all_change_points: Dict[str, AnalyzedSeries], notifiers: list
    ) -> list:

        if notifiers:
            for notifier in notifiers:
                await notifier.notify(all_change_points)

        reports = []
        for metric_name, analyzed_series in all_change_points.items():
            # analyzed_series.change_points_by_time = AnalyzedSeries.__group_change_points_by_time(analyzed_series.__series, analyzed_series.change_points)
            change_points = analyzed_series.change_points_by_time
            report = GitHubReport(analyzed_series.metric(metric_name), change_points)
            produced_report = await report.produce_report(self.name, ReportType.JSON)
            reports.append(json.loads(produced_report))


        # Merge all reports into a single list, collapsing metrics with the same
        # timestamp into a single entry.
        final_report = {}
        for report in reports:
            metric_report = report[self.name]

            # Simple case when we're adding the first metric report
            if not final_report:
                final_report[self.name] = metric_report
                continue

            for r in metric_report:
                # Each entry in metric_report can be for a timestamp we've never seen
                # before or for an existing timestamp.
                existing_timestamps = [c["time"] for c in final_report[self.name]]

                if r["time"] in existing_timestamps:
                    # Collapse the changes into the existing report
                    index = existing_timestamps.index(r["time"])
                    final_report[self.name][index]["changes"].extend(r["changes"])

                    # This should be impossible because we built the metric reports
                    # from a single series where an element has one set of attributes
                    # and potentially multiple metrics Check anyway.
                    if final_report[self.name][index]["attributes"] != r["attributes"]:
                        logging.error(
                            f"Attributes differ between metrics for timestamp {r['time']}"
                        )
                else:
                    # No existing report for this timestamp. Just add it.
                    final_report[self.name].append(r)

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


# If we hit the GitHub API rate limit, we should stop fetching for a while
# before retrying. This is a simple way to avoid hammering the API.
#
# The timestamp represents the time at which we should re-enable fetching.
GH_FETCH_RESET_TIMESTAMP = 0

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

    If we exceed the GitHub API rate limit, raise a GitHubRateLimitExceededError and
    disable fetching until the rate limit resets. Until the rate limits resets return
    None.
    """
    global GH_FETCH_RESET_TIMESTAMP
    if GH_FETCH_RESET_TIMESTAMP > datetime.now().timestamp():
        return None

    commit_msg = None
    client = httpx.AsyncClient()
    token = os.environ.get("GITHUB_TOKEN", None)
    response = await client.get(
        f"https://api.github.com/repos/{repo}/commits/{commit}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
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
            GH_FETCH_RESET_TIMESTAMP = int(reset)
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

        Return the updated attributes if a commit message was added, otherwise None.

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
            return attributes

        return None

    async def produce_report(self, test_name: str, report_type: ReportType):
        change_points = self._Report__change_points
        for cp in change_points:
            try:
                await GitHubReport.add_github_commit_msg(cp.attributes)
            except GitHubRateLimitExceededError as e:
                logging.error(e)
            except (httpx.ConnectTimeout, httpx.ConnectError) as e:
                logging.error(f"Connection to api.github.com failed: {e}")

        report = super().produce_report(test_name, report_type)
        return report


def _validate_cached_series(test_name, data, old_cp):
    for metric_name, m in data.items():
        metric_timestamps = m.timestamps
        metric_units = {metric_name: m.metric_unit}
        metric_data = {metric_name: m.metric_data}
        attributes = m.attributes
        series = Series(
            test_name,
            None,
            metric_timestamps,
            metric_units,
            metric_data,
            attributes,
        )
        cached_series = old_cp.__series[metric_name]
        if cached_series.test_name != series.test_name:
            logging.warning(
                "{}/{}: Cached test_name didn't match. Will discard cache. {} != {}".format(
                    test_name, metric_name, cached_series.test_name, series.test_name
                )
            )
            return False
        if len(cached_series.time) != len(series.time):
            logging.warning(
                "{}/{}: Cached test_name didn't match. Will discard cache. {} != {}".format(
                    test_name, metric_name, cached_series.test_name, series.test_name
                )
            )
            return False
    return True
