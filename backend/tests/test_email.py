from backend.auth.email import read_template_file


def test_email_template_substitution():
    f = "verify-email.html"
    verify_url = "myurl"
    out = read_template_file(f, verify_url=verify_url)
    assert verify_url in out
