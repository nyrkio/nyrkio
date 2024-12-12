from slack_sdk.webhook.async_client import AsyncWebhookClient

from backend.hunter.hunter.slack import (
    SlackNotification as HunterSlackNotification,
)

import logging


class SlackNotification(HunterSlackNotification):
    def __init__(self, series, data_selection_description, since):
        super().__init__(series, data_selection_description, since)

    def _SlackNotification__header(self):
        header_text = (
            "Nyrkiö has detected change points"
            if self.test_analyzed_series
            else "Nyrkiö did not detect any change points"
        )
        return self.__text_block("header", "plain_text", header_text)

    def _SlackNotification__get_change_emoji(self, test_name, change):
        """Nyrkiö doesn't have the concept of metric direction."""
        regression = change.forward_change_percent()
        if regression >= 0:
            return ":chart_with_upwards_trend:"
        else:
            return ":chart_with_downwards_trend:"


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
            logging.debug(f"Sending Slack notification to {self.channels}: {blocks}")
            response = await self.client.send(text="test (fallback)", blocks=blocks)
            if response.status_code != 200 or response.body != "ok":
                logging.error(
                    f"Failed to send Slack notification: {response.status_code}, {response.body}"
                )
