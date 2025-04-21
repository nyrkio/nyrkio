from slack_sdk.webhook.async_client import AsyncWebhookClient
from typing import Dict
from datetime import datetime
from backend.hunter.hunter.series import AnalyzedSeries
from backend.notifiers.abstract_notifier import AbstractNotifier, AbstractNotification

import logging
import json


class SlackNotification(AbstractNotification):
    def __init__(
        self,
        test_analyzed_series: Dict[str, AnalyzedSeries],
        since: datetime = None,
        base_url: str = "https://nyrkio.com/result/",
        public_base_url: str = None,
        public_tests: list = None,
    ):
        super().__init__(
            test_analyzed_series,
            since,
            base_url,
            public_base_url,
            public_tests,
        )

    def make_intro(self):
        self.intro = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": ".                              Changes since "
                                + self.since.strftime("%Y-%m-%dT%H:%M:%S"),
                                "style": {"italic": True},
                            }
                        ],
                    }
                ],
            }
        ]

    def get_intro(self):
        intro = self.intro
        self.intro = []
        return intro

    def create_dispatches(self):
        all_messages = self.create_message()
        # TODO: split all_messages to parts if too long
        dispatches = [all_messages]
        return dispatches

    def create_message(self):
        # https://api.slack.com/reference/block-kit/blocks#section
        slack_message = []
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

                    slack_message += [
                        {
                            "type": "rich_text",
                            "elements": [
                                {
                                    "type": "rich_text_section",
                                    "elements": [{"type": "text", "text": ". "}],
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "link",
                                            "text": short_commit,
                                            "url": "{}/commit/{}".format(
                                                git_repo, commit
                                            ),
                                            "style": {"bold": True},
                                        },
                                        {
                                            "type": "text",
                                            "text": "    {}".format(iso_date),
                                        },
                                    ],
                                },
                            ],
                        },
                    ]
                    for change in group.changes:
                        metric = change.metric
                        change_percent = change.forward_change_percent()
                        change_emoji = self._get_change_emoji(change)

                        slack_message += [
                            {
                                "type": "rich_text",
                                "elements": [
                                    {
                                        "type": "rich_text_section",
                                        "elements": [
                                            {"type": "emoji", "name": change_emoji},
                                            {
                                                "type": "link",
                                                "text": "{}: {} => {} %".format(
                                                    test_name,
                                                    metric,
                                                    round(change_percent, 1),
                                                ),
                                                "url": "{}?commit={}&timestamp={}#{}".format(
                                                    self.get_test_url(test_name),
                                                    commit,
                                                    timestamp,
                                                    metric,
                                                ),
                                            },
                                        ],
                                    }
                                ],
                            }
                        ]

        if not slack_message:
            return []
        else:
            return (
                self.get_intro()
                + slack_message
                + self._get_tests_with_insufficient_data()
            )

        return slack_message

    def _get_change_emoji(self, change):
        """Nyrkiö doesn't have the concept of metric direction."""
        regression = change.forward_change_percent()
        if regression >= 0:
            return "chart_with_upwards_trend"
        else:
            return "chart_with_downwards_trend"

    def _get_tests_with_insufficient_data(self):
        if len(self.tests_with_insufficient_data):
            txt_msg = ""
            delimiter = ""
            for test in self.tests_with_insufficient_data:
                txt_msg += "{}[{}]({})".format(delimiter, test, self.get_test_url(test))
                delimiter = ", "

            return [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
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


class SlackNotifier(AbstractNotifier):
    """
    An asynchroneous notifier for Slack that uses Hunter's SlackNotification
    to send messages.
    """

    def __init__(
        self,
        api_url,
        channels=None,
        since=None,
        base_url="https://nyrkio.com/result",
        public_base_url=None,
        public_tests=None,
    ):
        self.client = AsyncWebhookClient(api_url)
        self.channels = channels if channels is not None else []
        self.since = since
        self.base_url = base_url

    async def notify(self, series):
        dispatches = SlackNotification(
            series,
            since=self.since,
            base_url=self.base_url,
        ).create_dispatches()
        if len(dispatches) > 3:
            logging.error(
                "Change point summary would produce too many Slack notifications"
            )
            return

        for blocks in dispatches:
            if not blocks:
                continue

            # blocks = {"blocks": blocks}

            logging.debug(f"Sending Slack notification to {self.channels}: {blocks}")
            print(json.dumps(blocks))
            response = await self.client.send(text=json.dumps(blocks), blocks=blocks)
            if response.status_code != 200 or response.body != "ok":
                logging.error(
                    f"Failed to send Slack notification: {response.status_code}, {response.body}"
                )
