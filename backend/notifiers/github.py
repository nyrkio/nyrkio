import logging
import time

import httpx
import jwt


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
            logging.error(
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
    def create_body(results, pr_commit, changes) -> str:
        """
        Create a issue comment body from the test results and changes.
        """

        body = "Test name | Metric | Change" + "\n"
        body += "--- | --- | ---\n"

        anything_to_report = False
        for entry in results:
            for test_name, results in entry.items():
                test_metrics = collect_metrics(results)
                for m in test_metrics:
                    ch = find_changes(pr_commit, test_name, m, changes)
                    if ch is None:
                        ch = "N/A"
                    else:
                        ch = f"{ch:.2f}%"
                        anything_to_report = True

                    body += f"{test_name} | {m} | {ch}\n"

        if not anything_to_report:
            return "No performance changes detected. 🚀"

        return body

    async def notify(self, results, pr_commit, changes):
        """
        Post a comment to the pull request with the test results.

        Note that results and changes should only contain results for metrics
        that are not disabled.
        """
        access_token = await self._fetch_access_token()
        if not access_token:
            return

        body = GitHubCommentNotifier.create_body(results, pr_commit, changes)

        # Lookup the issue url from the pull request
        logging.debug(f"Fetching pull request: {self.pull_url}")
        response = await self.client.get(
            self.pull_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pull request: {response.status_code}")

        issue_url = response.json()["issue_url"]
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


def collect_metrics(results):
    metrics = set()
    for r in results:
        for m in r["metrics"]:
            metrics.add(m["name"])
    return metrics


def find_changes(pr_commit, test_name, metric, changes):
    for ch in changes:
        for t_name, data in ch.items():
            if t_name != test_name:
                continue

            for d in data:
                if d["attributes"]["git_commit"] != pr_commit:
                    continue

                for c in d["changes"]:
                    if c["metric"] == metric:
                        return c["forward_change_percent"]

    return None
