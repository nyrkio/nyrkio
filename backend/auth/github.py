import os

from httpx_oauth.clients.github import GitHubOAuth2

CLIENT_ID = "Iv1.829e5507d1b06795"
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", None)

github_oauth = GitHubOAuth2(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=["user", "user:email", "read:org"],
)
