from typing import Dict
from datetime import datetime
from pytz import UTC
from backend.hunter.hunter.series import AnalyzedSeries
from backend.api.public import extract_public_test_name

import httpx


class AbstractNotification:
    def __init__(
        self,
        test_analyzed_series: Dict[str, AnalyzedSeries],
        since: datetime = None,
        base_url: str = "https://nyrkio.com/result/",
        public_base_url: str = None,
        public_tests: list = None,
    ):
        self.git_repo = None
        """
        Used to smuggle out git_repo from the test data to the top level notifier class
        """
        self.since = since
        self.base_url = base_url
        self.tests_with_insufficient_data = []
        self.test_analyzed_series = dict()
        self.public_tests = public_tests if public_tests is not None else []
        self.public_base_url = public_base_url
        for test, series in test_analyzed_series.items():
            if series:
                self.test_analyzed_series[test] = series
            else:
                self.tests_with_insufficient_data.append(test)
        self.dates_change_points = {}
        for metric_name, analyzed_series in self.test_analyzed_series.items():
            test_name = analyzed_series.test_name()
            for group in analyzed_series.change_points_by_time:
                cpg_time = datetime.fromtimestamp(group.time, tz=UTC)
                if self.since and cpg_time < self.since:
                    continue
                date_str = cpg_time.strftime("%Y-%m-%dT%H:%M:%S")
                if test_name not in self.dates_change_points:
                    self.dates_change_points[test_name] = {}
                if metric_name not in self.dates_change_points[test_name]:
                    self.dates_change_points[test_name][metric_name] = {}
                self.dates_change_points[test_name][metric_name][date_str] = group

        self.make_intro()

    def get_test_url(self, test_name, attributes=None):
        if (
            attributes
            and self.public_base_url
            and self.public_tests
            and test_name in self.public_tests
        ):
            public_namespace = +extract_public_test_name(attributes)
            return self.public_base_url + public_namespace + "/" + test_name
        else:
            return self.base_url + test_name

    def make_intro(self):
        self.intro = "Changes since " + self.since.strftime("%Y-%m-%dT%H:%M:%S")

    def pop_intro(self):
        intro = self.intro
        self.intro = []
        return intro

    def get_intro(self):
        return self.intro

    def get_html_intro(self):
        return "<h2>" + self.intro + "</h2>\n"

    def get_markdown_intro(self):
        return "*" + self.intro + "*\n\n"

    # def create_dispatches(self):
    #     all_messages, git_repo = self.create_message()
    #     print(git_repo, all_messages)
    #     # TODO: split all_messages to parts if too long
    #     dispatches = [all_messages]
    #     return dispatches, git_repo

    def create_message(self):
        return self.create_markdown_message()

    def create_html_message(self):
        message = ""
        for test_name, all_metrics in self.dates_change_points.items():
            if not all_metrics:
                continue

            for metric_name, tests in all_metrics.items():
                if not tests:
                    continue

                for iso_date, group in tests.items():
                    if not group:
                        continue

                    timestamp = group.time
                    commit = group.attributes["git_commit"]
                    short_commit = commit[0:7]
                    git_repo = group.attributes["git_repo"]

                    message += '{}: <a href="{}/commit/{}">{}</a>:<br />'.format(
                        iso_date, git_repo, commit, short_commit
                    )
                    message += '{}: <a href="{}/commit/{}">{}</a>:<br />'.format(
                        iso_date, git_repo, commit, short_commit
                    )
                    for change in group.changes:
                        metric = change.metric
                        change_percent = change.forward_change_percent()
                        change_emoji = self._get_change_emoji(change)

                        url = "{}?commit={}&timestamp={}#{}".format(
                            self.get_test_url(test_name, group.attributes),
                            commit,
                            timestamp,
                            metric,
                        )
                        message += '{} {}: <a href="{}">{} => {} %</a><br />'.format(
                            change_emoji,
                            test_name,
                            url,
                            metric,
                            round(change_percent, 1),
                        )

        if not message:
            return ""
        else:
            return (
                self.get_html_intro()
                + message
                + self._get_html_tests_with_insufficient_data()
            )

    def create_markdown_message(self):
        message = ""
        table_head = "| Commit time         | Commit   | Test name           | Metric           | Change      |\n"
        table_head = (
            table_head
            + "|---------------------|----------|---------------------|------------------|-------------|\n"
        )
        commits = []
        git_repo = None
        for test_name, all_metrics in self.dates_change_points.items():
            if not all_metrics:
                continue
            for metric_name, tests in all_metrics.items():
                if not tests:
                    continue
                for iso_date, group in tests.items():
                    if not group:
                        continue

                    timestamp = group.time
                    commit = group.attributes["git_commit"]
                    short_commit = commit[0:7]
                    git_repo = (
                        group.attributes["git_repo"]
                        if group.attributes["git_repo"] is not None
                        else git_repo
                    )

                    # message += "{}: [{}]({}/commit/{})\n".format(
                    #     iso_date, short_commit, self.get_test_url(test_name), commit
                    # )
                    twocols = "| {} | [{}]({}/commit/{}) |".format(
                        str(iso_date)[:16], short_commit, git_repo, commit
                    )
                    commits.append(commit)

                    for change in group.changes:
                        metric = change.metric
                        change_percent = change.forward_change_percent()
                        change_emoji = self._get_change_emoji(change)

                        url = "{}?commit={}&timestamp={}#{}".format(
                            self.get_test_url(test_name),
                            commit,
                            timestamp,
                            metric,
                        )
                        message += (
                            twocols
                            + " {} | [{}]({}) | [{} {:+} %]({})\n".format(
                                test_name,
                                metric,
                                url,
                                change_emoji,
                                round(change_percent, 1),
                                url,
                            )
                        )
                        twocols = "|       |      |"
                        # message += "{} {}: [{} => {} %]({})\n".format(
                        #     change_emoji,
                        #     test_name,
                        #     metric,
                        #     round(change_percent, 1),
                        #     url,
                        # )

        footer = "\n\n[![Nyrkiö](https://nyrkio.com/p/logo/round/RedWhite/NyrkioLogo_Final_Logomark_RedTan_50x50.png)](https://nyrkio.com)"

        commit_footer = "<sub>Listing all commits mentioned in this message for search and backlink purposes:\n\n"
        commit_footer = commit_footer + ",".join(commits) + "</sub>"

        if not message:
            return "", None
        else:
            return (
                self.get_markdown_intro()
                + table_head
                + message
                + self._get_markdown_tests_with_insufficient_data()
                + footer
            ), git_repo

    def _get_change_emoji(self, change):
        """TODO: Use the direction field to sort regression vs improvement"""
        regression = change.forward_change_percent()
        if regression >= 0:
            return "📈"
        else:
            return "📉"

    def _get_html_tests_with_insufficient_data(self):
        if len(self.tests_with_insufficient_data):
            txt_msg = ""
            delimiter = ""
            for test in self.tests_with_insufficient_data:
                txt_msg += '{}<a href="{}">{}</a>'.format(
                    delimiter, self.get_test_url(test), test
                )
                delimiter = ", "

            return "Too few data to analyze:\n" + txt_msg
        else:
            return ""

    def _get_markdown_tests_with_insufficient_data(self):
        if len(self.tests_with_insufficient_data):
            txt_msg = ""
            delimiter = ""
            for test in self.tests_with_insufficient_data:
                txt_msg += "{}[{}]({})".format(delimiter, test, self.get_test_url(test))
                delimiter = ", "

            return "Too few data to analyze: " + txt_msg
        else:
            return ""


class AbstractNotifier:
    """
    Parent class for different notifiers
    """

    def __init__(
        self,
        api_url,
        channel_config,
        since: datetime = None,
        base_url: str = "https://nyrkio.com/result/",
        public_base_url: str = None,
        public_tests: list = None,
    ):
        self.since = since
        self.base_url = base_url
        self.public_base_url = public_base_url
        self.public_tests = public_tests if public_tests is not None else []

        self.client = httpx.AsyncClient()
        # self.headers = {"Authorization": f"Bearer {token['access_token']}"}

    # def create_notifications(self, series: Dict[str, AnalyzedSeries]):
    #     self.notification = AbstractNotification(
    #         series,
    #         self.since,
    #         self.base_url,
    #         self.public_base_url,
    #         self.public_tests,
    #     )
    #     self.dispatches = self.notification.create_dispatches()

    # async def send_notifications(self):
    #     return await self.client.post(self.api_url, headers=self.headers)

    async def notify(self, series):
        self.create_notifications(series)
        await self.send_notifications(git_repo=self.notification.git_repo)
