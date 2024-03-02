import httpx


class GitHubCommentNotifier:
    def __init__(self, access_token, repo, pull_number, changes):
        self.access_token = access_token
        self.pull_number = pull_number
        self.changes = changes

        # Remove https://github.com/ from the repo url
        owner, repo = repo.split("/")[3:]
        self.pull_url = (
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{self.pull_number}"
        )

    def notify(self):
        # Lookup the issue url from the pull request
        client = httpx.AsyncClient()
        response = client.get(self.pull_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pull request: {response.status_code}")

        issue_url = response.json()["issue_url"]
        response = client.post(
            f"{issue_url}/comments",
            json={"body": f"Test results: {self.changes}"},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        if response.status_code != 201:
            raise Exception(f"Failed to post comment: {response.status_code}")
