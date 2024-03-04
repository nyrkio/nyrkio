import logging
import time
from typing import List

import httpx
import jwt

from backend.api.model import TestResult


class GitHubCommentNotifier:
    def __init__(self, repo, pull_number):
        self.pull_number = pull_number

        # Remove https://github.com/ from the repo url
        self.owner, self.repo = repo.split("/")[3:]
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
    def create_body(results, changes) -> str:
        """
        Create a issue comment body from the test results and changes.
        """

        # Create a GitHub markdown table with all results
        body = """
        Test name | Metric | Baseline | Current | Change
        --- | --- | --- | --- | ---
        """

        for test_results, test_changes in zip(results, changes):
            for result, change in zip(test_results, test_changes):
                body += f"{result.test_name} | {result.metric} | {result.baseline} | {result.current} | {change}\n"
        
        return body

    async def notify(self, results: List[List[TestResult]], changes):
        """
        Post a comment to the pull request with the test results.

        Note that results and changes should only contain results for metrics
        that are not disabled.
        """
        access_token = await self._fetch_access_token()
        if not access_token:
            return

        body = GitHubCommentNotifier.create_body(results, changes)

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
