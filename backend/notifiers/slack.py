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
        base_url: str = "https://nyrkio.com/result/"
    ):
        self.data_selection_description = data_selection_description
        self.since = since
        self.base_url = base_url
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
                if test_name not in self.dates_change_points:
                    self.dates_change_points[test_name] = {}
                self.dates_change_points[test_name][date_str] = group

        self.make_intro()

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
        if len(self.dates_change_points.items()) == 0:
            return []

        slack_message = self.get_intro()
        for test_name, tests in self.dates_change_points.items():
            slack_message += [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "rich_text",
                                    "text": ". "
                                }
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "link",
                                    "text": test_name,
                                    "url": "{}{}".format(self.base_url, test_name),
                                }
                            ],
                        }
                    ],
                }
            ]

            for iso_date, group in tests.items():
                commit = group.attributes["git_commit"]
                short_commit = commit[0:7]
                git_repo = group.attributes["git_repo"]

                slack_message += [
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "link",
                                        "text": short_commit,
                                        "url": "{}/commit/{}".format(git_repo, commit),
                                        "style": {"bold": True},
                                    },
                                    {"type": "text", "text": "    {}".format(iso_date)},
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
                                            "text": ". {}: {} %".format(
                                                metric, round(change_percent, 1)
                                            ),
                                            "url": "{}{}?commit={}#{}".format(
                                                self.base_url, test_name, commit, metric
                                            ),
                                        },
                                    ],
                                }
                            ],
                        }
                    ]

        slack_message += self._get_tests_with_insufficient_data()
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
                txt_msg += "{}[{}]({}{})".format(
                    delimiter, test, self.base_url, test
                )
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


class SlackNotifier:
    """
    An asynchroneous notifier for Slack that uses Hunter's SlackNotification
    to send messages.
    """

    def __init__(self, url, channels, since=None, base_url="https://nyrkio.com/result"):
        self.client = AsyncWebhookClient(url)
        self.channels = channels
        self.since = since
        self.base_url = base_url

    async def notify(self, series):
        dispatches = SlackNotification(
            series,
            data_selection_description=None,
            since=self.since,
            base_url=self.base_url
        ).create_dispatches()
        if len(dispatches) > 3:
            logging.error(
                "Change point summary would produce too many Slack notifications"
            )
            return

        # test = [
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": "A message *with some bold text* and _some italicized text_.",
        #         },
        #     }
        # ]
        # test_block = [
        #     {
        #         "blocks": [
        #             {
        #                 "type": "section",
        #                 "text": {
        #                     "text": "A message *with some bold text* and _some italicized text_.",
        #                     "type": "mrkdwn",
        #                 },
        #                 "fields": [
        #                     {"type": "mrkdwn", "text": "*Priority*"},
        #                     {"type": "mrkdwn", "text": "*Type*"},
        #                     {"type": "plain_text", "text": "High"},
        #                     {"type": "plain_text", "text": "Silly"},
        #                 ],
        #             }
        #         ]
        #     }
        # ]
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
