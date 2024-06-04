from backend.notifiers.github import GitHubCommentNotifier


def test_github_comment_notifier():
    # Test the GitHubCommentNotifier class
    repo = "nyrkio/nyrkio"
    pull_number = 123
    notifier = GitHubCommentNotifier(repo, pull_number)
    assert notifier.pull_url == "https://api.github.com/repos/nyrkio/nyrkio/pulls/123"
