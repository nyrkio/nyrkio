# Authentication

Nyrkiö uses JWT (JSON Web Token) authentication for API access.

## Getting a Token

### GitHub OAuth (Recommended)

1. Visit https://nyrkio.com (or your local instance)
2. Click "Sign in with GitHub"
3. Authorize the Nyrkiö application
4. Navigate to Settings → API Tokens
5. Copy your API token

### Email Registration

1. Visit the registration page
2. Enter your email address
3. Check your email for verification link
4. Complete registration
5. Navigate to Settings → API Tokens

## Using Your Token

### Authorization Header

Include your token in the `Authorization` header:

```bash
curl -X GET "https://api.nyrkio.com/api/v0/result/my-test" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Python Example

```python
import requests

token = "YOUR_TOKEN_HERE"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "https://api.nyrkio.com/api/v0/result/my-test",
    headers=headers
)
```

### JavaScript Example

```javascript
const token = "YOUR_TOKEN_HERE";

fetch("https://api.nyrkio.com/api/v0/result/my-test", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Token Management

### Token Security

- **Never commit tokens** to version control
- Store tokens in environment variables
- Use CI/CD secret management for automation
- Rotate tokens regularly

### Token Scope

Tokens have full access to:
- Submit test results
- View your test data
- Configure tests
- Manage notifications
- Organization resources (if member)

### Revoking Tokens

To revoke a token:
1. Go to Settings → API Tokens
2. Click "Revoke" next to the token
3. Confirm revocation

The token will immediately stop working.

## GitHub Actions

Store your token as a GitHub secret:

1. Go to repository Settings → Secrets
2. Create secret named `NYRKIO_TOKEN`
3. Use in workflows:

```yaml
- name: Submit Results
  env:
    NYRKIO_TOKEN: ${{ secrets.NYRKIO_TOKEN }}
  run: |
    curl -X POST "https://api.nyrkio.com/api/v0/result/test-name" \
      -H "Authorization: Bearer $NYRKIO_TOKEN" \
      -d @results.json
```

## Organization Tokens

Organization-level tokens can be created by organization admins:

1. Navigate to organization settings
2. Go to API Tokens section
3. Create organization token
4. Set permissions and expiration

Organization tokens allow:
- Submitting results to organization tests
- Viewing organization-wide data
- Managing organization resources (with admin permissions)

## Token Expiration

Tokens can be configured with expiration:
- **Default**: No expiration
- **Custom**: 30 days, 90 days, 1 year, or custom date

Expired tokens will return `401 Unauthorized` errors.

## Error Responses

### 401 Unauthorized

Token is missing, invalid, or expired:

```json
{
  "detail": "Could not validate credentials"
}
```

**Solution**: Check token is correct and not expired.

### 403 Forbidden

Token is valid but lacks permission:

```json
{
  "detail": "Not authorized to access this resource"
}
```

**Solution**: Check you have access to the requested resource.

## Rate Limiting

API requests are rate-limited per token:
- **Default**: 1000 requests per hour
- **Organization**: 5000 requests per hour

Rate limit headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

When rate limited, API returns `429 Too Many Requests`.
