import os
from typing import Optional, List

from httpx_oauth.clients.openid import OpenID

CLIENT_ID = os.environ.get("ONE_LOGIN_CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("ONE_LOGIN_CLIENT_SECRET", None)
ONELOGIN_REDIRECT_URI = "https://nyrkio.com/auth/onelogin/mycallback"
ONELOGIN_OIDC_HOST = "openid-connect.onelogin.com"

BASE_SCOPES = ["openid", "email"]


class OneLoginOAuth2(OpenID):
    """OAuth2 client for OneLogin."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        onelogin_domain: str,
        scopes: Optional[List[str]] = BASE_SCOPES,
        name: str = "onelogin",
    ):
        """
        Args:
            client_id: The client ID provided by the OAuth2 provider.
            client_secret: The client secret provided by the OAuth2 provider.
            okta_domain: The Okta organization domain.
            scopes: The default scopes to be used in the authorization URL.
            name: A unique name for the OAuth2 client.
        """
        super().__init__(
            client_id,
            client_secret,
            f"https://{onelogin_domain}/oidc/2/.well-known/openid-configuration",
            name=name,
            base_scopes=scopes,
        )


print(
    CLIENT_SECRET[:3] if CLIENT_SECRET is not None else "ONE_LOGIN_CLIENT_SECRET=None"
)
print(CLIENT_ID)
onelogin_oauth = OneLoginOAuth2(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    onelogin_domain="nyrkio.onelogin.com",
    scopes=["user", "user:email", "read:org"],
)
