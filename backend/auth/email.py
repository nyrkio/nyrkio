import logging
import os
from pathlib import Path
import httpx
from string import Template

POSTMARK_API_KEY = os.environ.get("POSTMARK_API_KEY", None)


# TODO(matt) should be async?
def read_template_file(template_file: str, **kwargs):
    path = Path(__file__).parent / f"templates/{template_file}"
    with open(path, "r") as f:
        t = Template(f.read())
        return t.substitute(**kwargs)


async def send_email(email: str, token: str, subject: str, msg: str):
    """
    Send an email to a user with a verification token.
    """
    return 

    with httpx.Client() as client:
        url = "https://api.postmarkapp.com/email"
        response = client.post(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": POSTMARK_API_KEY,
            },
            json={
                "From": "matt@nyrkio.com",
                "To": email,
                "Subject": subject,
                "HtmlBody": msg,
                "MessageStream": "outbound",
            },
        )
        if response.status_code != 200:
            logging.error(f"Failed to send email: {response.status_code}")
