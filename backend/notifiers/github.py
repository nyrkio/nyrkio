from typing import Dict, Union
from otava.series import AnalyzedSeries
import logging
import time
from datetime import datetime
import os

import httpx
import jwt
import urllib.parse

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
            token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

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
    def __init__(self, repo, pull_number, public_base_url=None, public_tests=[]):
        if public_base_url is not None and public_base_url[-1] == "/":
            public_base_url = public_base_url[:-1]
        self.pull_number = pull_number
        self.public_base_url = public_base_url
        self.public_tests = public_tests

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

    def create_body(self, results, pr_commit, changes, base_url) -> str:
        """
        Create a issue comment body from the test results and changes.
        """
        header = "**Nyrkiö Report for Commit**: " + pr_commit
        body = "Test name | Metric | Change" + "\n"
        body += "--- | --- | ---\n"
        green_footer = "\n\n[![Nyrkiö](https://nyrkio.com/p/logo/round/Logomark_GithubGreen3-50x50.png)](https://nyrkio.com)"
        red_footer = "\n\n[![Nyrkiö](https://nyrkio.com/p/logo/round/Logomark_RedBrown2-thick-50x50.png)](https://nyrkio.com)"
        total_tests = len(results)
        total_metrics = 0
        total_changes = 0

        anything_to_report = False
        for entry in results:
            for test_name, results in entry.items():
                test_metrics = collect_metrics(results)
                public_prefix = get_public_prefix(results)
                base_commit = get_base_commit(pr_commit, results)
                base_commit_info = ""
                if base_commit is not None:
                    base_sha = base_commit["id"]
                    base_commit_info = f" Base commit {base_sha}"
                    if base_commit.get("timestamp", False) and isinstance(
                        base_commit["timestamp"], int
                    ):
                        base_date = datetime.fromtimestamp(
                            base_commit["timestamp"]
                        ).strftime("%a %-d %b, %Y")
                        base_commit_info += f" from {base_date}"
                for m, direction in test_metrics.items():
                    c = FeedbackTextDecoration(direction)
                    ch_num, mb, ma, ch_str = find_changes(
                        pr_commit, test_name, m, changes
                    )
                    total_metrics += 1
                    if ch_num is not None:
                        anything_to_report = True
                        total_changes += 1

                        burl = base_url
                        # print(test_name)
                        if test_name in self.public_tests:
                            burl = self.public_base_url + "/" + public_prefix

                        change = c.render(ch_num, f"{ch_str} % ({mb} → {ma})")
                        body += f"[{test_name}]({burl}{test_name}) | [{m}]({burl}{test_name}#{m}) {c.arrow} |{change}\n"

        if not anything_to_report:
            return (
                header
                + "\n\n"
                + "No performance changes detected.\n"
                + "Remember that Nyrkiö results become more precise when more commits are merged.\n"
                + f"So [please check again]({base_url}) in a few days.\n\n"
                + green_footer
                + f"    {total_changes} changes / {total_tests} tests & {total_metrics} metrics."
                + base_commit_info
            )

        return (
            header
            + base_commit_info
            + "\n\n"
            + body
            + red_footer
            + f"    {total_changes} changes / {total_tests} tests & {total_metrics} metrics."
            + base_commit_info
        )

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

        body = self.create_body(results, pr_commit, changes, base_url)
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
        logging.debug(recent_comments)
        for c in recent_comments:
            # Find comments from the specific PR
            logging.debug(
                f"matching my pull_number = {self.pull_number} and {c['issue_url']}"
            )
            if c["issue_url"].endswith(f"issues/{self.pull_number}"):
                # Find a comment by this app
                if c["user"]["login"] == "nyrkio[bot]":
                    logging.debug(c["body"])
                    # Find the comment with change detection results
                    if "body" in c and c["body"].startswith(
                        "**Nyrkiö Report for Commit"
                    ):
                        return c


def collect_metrics(results):
    metrics = {}
    for r in results:
        for m in r["metrics"]:
            metrics[m["name"]] = m.get("direction")
    return metrics


def get_public_prefix(results):
    git_repo = results[-1]["attributes"]["git_repo"]
    branch = results[-1]["attributes"]["branch"]
    return (
        urllib.parse.quote_plus(git_repo) + "/" + urllib.parse.quote_plus(branch) + "/"
    )


def _custom_round(x):
    if isinstance(x, str):
        if "." in x:
            while x[-1] == "0":
                x = x[:-1]

    if str(x) != str(float(x)) or isinstance(x, int):
        return x
    x = float(x)

    if abs(x) < 1000:
        if abs(x) < 1:
            return f"{x:.1f}" if x % 1 == 0.0 else f"{x:.3g}"

        return f"{x:.1f}" if x % 1 == 0.0 else f"{x:.4g}"
    else:
        return f"{x:.0f}"


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
                            float(c["forward_change_percent"]),
                            _custom_round(c["mean_before"]),
                            _custom_round(c["mean_after"]),
                            _custom_round(c["forward_change_percent"]),
                        )
                    else:
                        print(str(c))

    return None, None, None, None


class FeedbackTextDecoration:
    def __init__(self, direction: str = None):
        self.set_map(direction)

    def set_map(self, direction):
        if direction == "lower_is_better":
            self.pos = "-"
            self.neg = "+"
            self.arrow = "⇓"
            self.emoji = lambda x: "😻" if x < 0.0 else "🙀"
        elif direction == "higher_is_better":
            self.pos = "+"
            self.neg = "-"
            self.arrow = "⇑"
            self.emoji = lambda x: "😻" if x > 0.0 else "🙀"
        else:  # None / default
            self.pos = ""
            self.neg = ""
            self.arrow = ""
            self.emoji = lambda x: ""

    def color(self, value: Union[float, int]):
        if float(value) < 0.0:
            return f"{self.neg} "
        else:
            return f"{self.pos} "

    def render(self, value: Union[float, int], txt: str):
        return txt + self.emoji(value)


def get_base_commit(pr_commit, results):
    """
    Sample

    "base_commit": {
        "author": {
            "name": "Henrik Ingo",
            "username": "henrikingo",
            "email": "henrik@nyrk.io"
        },
        "committer": {
            "name": "Henrik Ingo",
            "username": "henrikingo",
            "email": "henrik@nyrk.io"
        },
        "id": "e8f32fe51999005f5a958136b86d80c0a445ad14",
        "message": "debug env",
        "timestamp": "2025-11-04T21:48:41Z",
        "url": "https://api.github.com/repos/nyrkio/change-detection/git/commits/e8f32fe51999005f5a958136b86d80c0a445ad14",
        "repo": "change-detection",
        "repoUrl": "https://github.com/nyrkio/change-detection/commit/e8f32fe51999005f5a958136b86d80c0a445ad14",
        "branch": "master"
    }
    """
    for r in results:
        if r["attributes"]["git_commit"] == pr_commit:
            return r.get("extra_info", {}).get("base_commit", None)
    return None
