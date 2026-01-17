from fastapi_users.authentication.transport.bearer import BearerTransport
from fastapi.security.oauth2 import OAuth2PasswordBearer

class BearerOrBodyTransport(BearerTransport):
    def __init__(self, tokenUrl: str):
        self.scheme= OAuth2BearerOrBody(tokenUrl, auto_error=False)

# This extends BearerTransport to also accept requests where a POST request
# body includes a key `access_token`, as specified in OAuth2 RFC.
class OAuth2BearerOrBody(OAuth2PasswordBearer):
      """Checks form body first, then Authorization header, ok if either has a valid token."""

      async def __call__(self, request: Request) -> Optional[str]:
          # POST body (aka form field) access_token
          # Note, strictly speaking the spec also requires
          # request.headers.get("content-type") == "application/x-www-form-urlencoded"
          # But we allow json since we work with json anyway

          if request.method in ("POST", "PUT", "PATCH"):
              form = await request.form()
              token = form.get("access_token"):
              if token:
                  return token

          # Try Authorization: Bearer header
          authorization = request.headers.get("Authorization")
          if authorization and authorization.lower().startswith("bearer "):
              return authorization[7:]
          if not authorization:
              if self.auto_error:
                  raise self.make_not_authenticated_error()
          return None
