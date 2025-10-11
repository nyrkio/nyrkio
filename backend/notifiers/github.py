from typing import Dict
from backend.hunter.hunter.series import AnalyzedSeries
import logging
import time
from datetime import datetime
import os

import httpx
import jwt

from backend.notifiers.abstract_notifier import AbstractNotifier, AbstractNotification
from backend.db.db import DBStore
from backend.auth.github import CLIENT_ID

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)


class GitHubIssueNotification(AbstractNotification):
    pass


class GitHubIssueNotifier(AbstractNotifier):
    """
    File one GitHub issue per commit, if commit has one or more regressions
    """

    def __init__(
        self,
        api_url,
        gh_config,
        since: datetime = None,
        base_url: str = "https://nyrkio.com/result/",
        public_base_url: str = None,
        public_tests: list = None,
    ):
        super().__init__(
            api_url,
            gh_config,
            since,
            base_url,
            public_base_url,
            public_tests,
        )
        self.github = gh_config
        self.token_url = gh_config["installation"]["access_tokens_url"]
        self.client = httpx.AsyncClient()
        self.owner = gh_config["installation"]["account"]["login"]
        # Note that repo name will be filled in later
        self.api_url = api_url.format(self.owner, "{}")

    async def send_notifications(self, message, git_repo=None):
        self.gh_access_token = await fetch_access_token(self.token_url)
        self.headers = {"Authorization": f"Bearer {self.gh_access_token}"}
        payload = {
            "title": "Nyrkiö detected change points, on {}".format(
                str(datetime.today())[:16]
            ),
            "body": message,
            "labels": ["nyrkio"],
        }

        if message:
            repo_name = git_repo.split("/")[-1]
            url = self.api_url.format(repo_name)
            response = await self.client.post(url, json=payload, headers=self.headers)

            if response.status_code >= 400:
                logging.error(
                    f"Failed to post issue about performance change to GitHub: {response.status_code}: {response.text}"
                )
                logging.error(f"URL was: {url}")

            data = response.json()
            # print(data)
            if "url" in data:
                issue_url = data["url"]
                for c in self.notification.commits:
                    for test_name, obj in self.notification.reported_commits[c].items():
                        if (
                            "issue_url" not in obj
                            and obj["date"] == self.notification.batch_timestamp
                        ):
                            obj["issue_url"] = issue_url
            return data

    def create_notifications(self, series: Dict[str, AnalyzedSeries], reported_commits):
        self.notification = GitHubIssueNotification(
            series,
            self.since,
            self.base_url,
            self.public_base_url,
            self.public_tests,
            reported_commits,
        )
        message, git_repo = self.notification.create_message()
        self.message = message
        return message, git_repo

    def create_markdown_message(self):
        mdmessage = super().create_markdown_message()
        return mdmessage

    async def notify(self, series, user_or_org_id):
        reported_commits = None
        if user_or_org_id is not None:
            db = DBStore()
            reported_commits = await db.get_reported_commits(user_or_org_id)
            if reported_commits is None:
                reported_commits = {}

        message, git_repo = self.create_notifications(series, reported_commits)
        await self.send_notifications(message, git_repo=git_repo)
        if reported_commits is not None:
            await db.save_reported_commits(reported_commits, user_or_org_id)


async def fetch_access_token(
    token_url=None, expiration_seconds=600, installation_id=None
):
    """Grab an access token for the Nyrkio app installation."""
    # See https://docs.github.com/
    pem = "/usr/src/backend/keys/nyrkio.pem"
    try:
        with open(pem, "rb") as pem_file:
            signing_key = pem_file.read()
    except FileNotFoundError:
        logging.error(f"Could not find GitHub app pem file: {pem}")
        raise

    payload = {
        # Issued at time
        "iat": int(time.time()),
        # JWT expiration time (10 minutes maximum)
        "exp": int(time.time()) + expiration_seconds,
        # GitHub App's identifier
        "iss": CLIENT_ID,  # ,
    }

    encoded_jwt = jwt.encode(payload, signing_key, algorithm="RS256")

    client = httpx.AsyncClient()

    if token_url is None:
        if installation_id is None:
            raise ValueError("either a token_url or an installation_id is required.")
        else:
            token_url = (
                "https://api.github.com/app/installations/{installation_id}/access_tokens",
            )

    response = await client.post(
        token_url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {encoded_jwt}",
        },
    )
    if response.status_code != 201:
        logging.error(
            f"Failed to fetch access token: {response.status_code}: {response.json()}"
        )
        return None

    access_token = response.json()["token"]
    return access_token


class GitHubCommentNotifier:
    def __init__(self, repo, pull_number):
        self.pull_number = pull_number

        self.owner, self.repo = repo.split("/")
        self.pull_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{self.pull_number}"

        self.client = httpx.AsyncClient()

    async def _fetch_access_token(self):
        """Grab an access token for the Nyrkio app installation."""
        installation_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}/installation"
        )

        # See https://docs.github.com/
        pem = "/usr/src/backend/keys/nyrkio.pem"
        try:
            with open(pem, "rb") as pem_file:
                signing_key = pem_file.read()
        except FileNotFoundError:
            logging.error(f"Could not find GitHub app pem file: {pem}")
            raise

        payload = {
            # Issued at time
            "iat": int(time.time()),
            # JWT expiration time (10 minutes maximum)
            "exp": int(time.time()) + 600,
            # GitHub App's identifier
            "iss": 699959,
        }

        encoded_jwt = jwt.encode(payload, signing_key, algorithm="RS256")

        logging.debug(f"Fetching installation: {installation_url}")
        response = await self.client.get(
            installation_url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {encoded_jwt}",
            },
        )
        if response.status_code != 200:
            logging.info(
                f"Failed to fetch installation: {response.status_code}: {response.json()}"
            )
            return None

        installation_id = response.json()["id"]
        response = await self.client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {encoded_jwt}",
            },
        )
        if response.status_code != 201:
            logging.error(
                f"Failed to fetch access token: {response.status_code}: {response.json()}"
            )
            return None

        access_token = response.json()["token"]
        return access_token

    @staticmethod
    def create_body(results, pr_commit, changes, base_url) -> str:
        """
        Create a issue comment body from the test results and changes.
        """

        header = "**Nyrkiö Report for Commit**: " + pr_commit + "\n\n"
        body = "Test name | Metric | Change" + "\n"
        body += "--- | --- | ---\n"
        green_footer = "\n\n[![Nyrkiö](https://nyrkio.com/p/logo/round/Logomark_GithubGreen-50x50.png)](https://nyrkio.com)"
        red_footer = "\n\n[![Nyrkiö](https://nyrkio.com/p/logo/round/Logomark_RedBrown2-thick-50x50.png)](https://nyrkio.com)"

        anything_to_report = False
        for entry in results:
            for test_name, results in entry.items():
                test_metrics = collect_metrics(results)
                for m in test_metrics:
                    ch, mb, ma = find_changes(pr_commit, test_name, m, changes)
                    if ch is not None:
                        anything_to_report = True

                        body += f"[{test_name}]({base_url}{test_name}) | [{m}]({base_url}{test_name}#{m}) | {ch} % ({mb} → {ma})\n"

        if not anything_to_report:
            return (
                header
                + "No performance changes detected.\n\nRemember that Nyrkiö results become more precise when more commits are merged. So please check back in a few days."
                + green_footer
            )

        return header + body + red_footer

    async def notify(
        self, results, pr_commit, changes, base_url: str = "https://nyrkio.com/result/"
    ):
        """
        Post a comment to the pull request with the test results.

        Note that results and changes should only contain results for metrics
        that are not disabled.
        """
        access_token = await self._fetch_access_token()
        if not access_token:
            return

        body = GitHubCommentNotifier.create_body(results, pr_commit, changes, base_url)
        old_comment = await self.find_existing_comment(access_token)
        if old_comment:
            old_comment_id = old_comment["id"]
            old_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/comments/{old_comment_id}"
            logging.debug(f"Updating existing comment at {old_url}")
            response = await self.client.patch(
                f"{old_url}",
                json={"body": body},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code > 201:
                raise Exception(f"Failed to post comment: {response.status_code}")
        else:
            # Lookup the issue url from the pull request
            issue_url = await self.get_issue_url(access_token)
            logging.debug(f"Posting comment to {issue_url}/comments")
            response = await self.client.post(
                f"{issue_url}/comments",
                json={"body": body},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code != 201:
                raise Exception(f"Failed to post comment: {response.status_code}")

    async def get_issue_url(self, access_token):
        logging.debug(f"Fetching pull request: {self.pull_url}")
        response = await self.client.get(
            self.pull_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pull request: {response.status_code}")

        issue_url = response.json()["issue_url"]
        return issue_url

    async def list_issue_comments(self, access_token):
        comments_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{self.pull_number}/comments?sort=updated&per_page=100&direction=desc"
        logging.debug(f"Fetching 100 newest repo comments: {comments_url}")
        response = await self.client.get(
            comments_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pull request: {response.status_code}")

        res = response.json()
        # logging.info(res)
        res = res if isinstance(res, list) else [res]
        return res

    async def find_existing_comment(self, access_token):
        recent_comments = await self.list_issue_comments(access_token)
        logging.info(f"Received {len(recent_comments)} comments from GitHub.")
        logging.info(recent_comments)
        for c in recent_comments:
            # Find comments from the specific PR
            logging.info(
                f"matching my pull_number = {self.pull_number} and {c['issue_url']}"
            )
            if c["issue_url"].endswith(f"issues/{self.pull_number}"):
                # Find a comment by this app
                logging.info("client_id")
                if c["user"]["login"] == "nyrkio[bot]":
                    logging.info(c["body"])
                    # Find the comment with change detection results
                    if "body" in c and c["body"].startswith(
                        "**Nyrkiö Report for Commit"
                    ):
                        return c


def collect_metrics(results):
    metrics = set()
    for r in results:
        for m in r["metrics"]:
            metrics.add(m["name"])
    return metrics


def find_changes(pr_commit, test_name, metric, changes):
    for ch in changes:
        for t_name, data in ch.items():
            if False or t_name != test_name:
                continue

            for d in data:
                if d["attributes"]["git_commit"] != pr_commit:
                    continue

                for c in d["changes"]:
                    if c["metric"] == metric:
                        return (
                            c["forward_change_percent"],
                            c["mean_before"],
                            c["mean_after"],
                        )

    return None, None, None
