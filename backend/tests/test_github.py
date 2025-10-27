from backend.notifiers.github import GitHubCommentNotifier, _custom_round


def test_github_comment_notifier():
    # Test the GitHubCommentNotifier class
    repo = "nyrkio/nyrkio"
    pull_number = 123
    notifier = GitHubCommentNotifier(repo, pull_number)
    assert notifier.pull_url == "https://api.github.com/repos/nyrkio/nyrkio/pulls/123"


def test_custom_round():
    assert _custom_round(1) == int(1)
    assert _custom_round(1.0) == str("1.0")
    assert _custom_round(10.0) == str("10.0")
    assert _custom_round(1.01) == str("1.01")
    assert _custom_round(0.012) == str("0.012")
    assert _custom_round(1.012) == str("1.012")
    assert _custom_round(0.0123) == str("0.0123")
    assert _custom_round(1.0123) == str("1.012")
    assert _custom_round(0.01234) == str("0.0123")
    assert _custom_round(1.01234) == str("1.012")
    assert _custom_round(0.012323) == str("0.0123")
    assert _custom_round(0.0123456) == str("0.0123")
    # assert _custom_round(1.012345) == str("1.012")
    assert _custom_round(1234567) == int(1234567)
    assert _custom_round(1234567890) == 1234567890
    assert _custom_round(1234567890.0) == str("1234567890")
    assert _custom_round(123456.789) == str("123457")
