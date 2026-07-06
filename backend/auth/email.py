import logging
import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import httpx
from string import Template

POSTMARK_API_KEY = os.environ.get("POSTMARK_API_KEY", None)

# When set, emails are sent via plain SMTP (e.g. to a local Mailhog
# instance) instead of the Postmark HTTP API. Intended for local dev only.
SMTP_HOST = os.environ.get("SMTP_HOST", None)
SMTP_PORT = int(os.environ.get("SMTP_PORT", 1025))

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
    if SMTP_HOST:
        _send_email_smtp(email, subject, msg)
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
                "From": "helloworld@nyrkio.com",
                "To": email,
                # "To": "henrik@nyrkio.com",
                "Subject": subject,
                "HtmlBody": msg,
                "MessageStream": "outbound",
            },
        )
        if response.status_code != 200:
            logging.error(f"Failed to send email: {response.status_code}")


def _send_email_smtp(email: str, subject: str, msg: str):
    """
    Send an email over plain SMTP, e.g. to a local Mailhog instance.
    """
    message = MIMEText(msg, "html")
    message["Subject"] = subject
    message["From"] = "helloworld@nyrkio.com"
    message["To"] = email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(message["From"], [email], message.as_string())
    except OSError as e:
        logging.error(f"Failed to send email via SMTP {SMTP_HOST}:{SMTP_PORT}: {e}")
