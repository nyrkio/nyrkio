from slack_sdk.webhook.async_client import AsyncWebhookClient
from typing import Dict
from datetime import datetime
from pytz import UTC
from backend.hunter.hunter.series import AnalyzedSeries

import logging
import json

class SlackNotification:
    def __init__(
        self,
        test_analyzed_series: Dict[str, AnalyzedSeries],
        data_selection_description: str = None,
        since: datetime = None,
    ):
        self.data_selection_description = data_selection_description
        self.since = since
        self.tests_with_insufficient_data = []
        self.test_analyzed_series = dict()
        for test, series in test_analyzed_series.items():
            if series:
                self.test_analyzed_series[test] = series
            else:
                self.tests_with_insufficient_data.append(test)

        self.dates_change_points = {}
        for test_name, analyzed_series in self.test_analyzed_series.items():
            for group in analyzed_series.change_points_by_time:
                cpg_time = datetime.fromtimestamp(group.time, tz=UTC)
                if self.since and cpg_time < self.since:
                    continue
                date_str = cpg_time.strftime("%Y-%m-%dT%H:%M:%S")
                if date_str not in self.dates_change_points:
                    self.dates_change_points[date_str] = {}
                self.dates_change_points[date_str][test_name] = group

    def create_dispatches(self):
        all_messages = self.create_message()
        # TODO: split all_messages to parts if too long
        dispatches = [all_messages]
        return dispatches

    def create_message(self):
        # https://api.slack.com/reference/block-kit/blocks#section
        slack_message = {
            "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Changes since: " + self.since.strftime("%Y-%m-%dT%H:%M:%S"),
                },
                "fields": [],
            }]
        }

        for iso_date, tests in self.dates_change_points.items():
            test_name = list(tests.keys())[0]
            commit = tests[test_name].attributes["git_commit"]
            short_commit = commit[0:6]
            git_repo = tests[test_name].attributes["git_repo"]

            slack_message["blocks"][0]["fields"] += [
                {
                        "type": "mrkdwn",
                        "text": iso_date,
                },
                {
                        "type": "mrkdwn",
                        "text": "[{}]({}/commit/{})".format(short_commit, git_repo, commit),
                },
            ]
            for test_name, group in tests.items():
                for change in group.changes:
                    metric = change.metric
                    change_percent = change.forward_change_percent()
                    change_emoji = self._get_change_emoji(change)

                    slack_message["blocks"][0]["fields"] += [
                        {
                                "type": "mrkdwn",
                                "text": "[{}](https:/nyrkio.com/result/example?commit={})".format(
                                    test_name, commit
                                )
                        },
                        {
                                "type": "mrkdwn",
                                "text": "[{} {}: {}](https:/nyrkio.com/result/{}?commit={}#{})".format(
                                    change_emoji,
                                    metric,
                                    round(change_percent, 1),
                                    test_name,
                                    commit,
                                    metric,
                                )

                        }
                    ]

        slack_message["blocks"][0]["fields"] += self._get_tests_with_insufficient_data()
        return slack_message

    def _get_change_emoji(self, change):
        """Nyrkiö doesn't have the concept of metric direction."""
        regression = change.forward_change_percent()
        if regression >= 0:
            return ":chart_with_upwards_trend:"
        else:
            return ":chart_with_downwards_trend:"

    def _get_tests_with_insufficient_data(self):
        if len(self.tests_with_insufficient_data):
            txt_msg = ""
            delimiter = ""
            for test in self.tests_with_insufficient_data:
                txt_msg += "{}[{}](https:/nyrkio.com/result/{})".format(
                    delimiter, test, test
                )
                delimiter = ", "

            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Too few data to analyze:",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": txt_msg,
                    },
                },
            ]
        else:
            return []


class SlackNotifier:
    """
    An asynchroneous notifier for Slack that uses Hunter's SlackNotification
    to send messages.
    """

    def __init__(self, url, channels, since=None):
        self.client = AsyncWebhookClient(url)
        self.channels = channels
        self.since = since

    async def notify(self, series):
        dispatches = SlackNotification(
            series,
            data_selection_description=None,
            since=self.since,
        ).create_dispatches()
        if len(dispatches) > 3:
            logging.error(
                "Change point summary would produce too many Slack notifications"
            )
            return

        for blocks in dispatches:
            blocks_json = json.dumps(blocks)
            logging.debug(f"Sending Slack notification to {self.channels}: {blocks_json}")
            print(blocks_json)
            response = await self.client.send(text="test (fallback)", blocks=blocks_json)
            if response.status_code != 200 or response.body != "ok":
                logging.error(
                    f"Failed to send Slack notification: {response.status_code}, {response.body}"
                )
