# Integration Test Setup Requirements

## Prerequisites

### 1. Test User Setup

Integration tests require a verified test user in the database.

**Create test user:**
```bash
curl -X POST http://localhost:8001/api/v0/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123", "username": "testuser"}'
```

**Verify test user** (REQUIRED - users must be verified to login):
```bash
mongosh nyrkiodb --eval 'db.User.updateOne({email: "test@example.com"}, {$set: {is_verified: true}})'
```

**Test login works:**
```bash
curl -X POST http://localhost:8001/api/v0/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123"
```

Should return a JWT token.

### 2. Server Requirements

**Backend server must be running:**
```bash
# From backend directory
python3 ../etc/nyrkio_backend.py start
```

Should be accessible at: http://localhost:8001/docs

**Frontend dev server must be running:**
```bash
# From frontend directory
npm run dev
```

Should be accessible at: http://localhost:5173

### 3. Database Requirements

- MongoDB must be running on localhost:27017
- Database name: `nyrkiodb`
- Collection: `User` (capital U)

## Running Tests

**With servers already running:**
```bash
npx playwright test --config=playwright.config.integration.ts
```

**Run specific test file:**
```bash
npx playwright test tests/integration/ui-dashboard.integration.ts --config=playwright.config.integration.ts
```

**Run single test:**
```bash
npx playwright test tests/integration/ui-dashboard.integration.ts --config=playwright.config.integration.ts --grep "test name"
```

**Run in UI mode (for debugging):**
```bash
npx playwright test --config=playwright.config.integration.ts --ui
```

## Known Issues

### Login Redirect Issue

The login form uses `window.location.href = "/"` for redirection after successful login. In Playwright tests, this redirection may not fire reliably, causing `page.waitForURL("/")` to timeout.

**Workaround options:**
1. Wait for authentication state instead of URL change
2. Manually navigate after login completes
3. Use `page.waitForLoadState()` instead of `page.waitForURL()`

### Test Environment Variables

Tests use these default credentials (can be overridden):
```javascript
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123
```

To override:
```bash
TEST_USER_EMAIL=other@example.com TEST_USER_PASSWORD=otherpass npx playwright test
```

## Troubleshooting

### "LOGIN_USER_NOT_VERIFIED" error

User exists but isn't verified. Run the mongosh command to verify the user.

### "net::ERR_CONNECTION_REFUSED"

Frontend or backend server not running. Check that both servers are accessible.

### Timeout waiting for navigation

Login redirect not firing. This is a known issue - see "Known Issues" section above.

### Tests fail with "Cannot find module '@playwright/test'"

Install Playwright:
```bash
npm install --save-dev @playwright/test
npx playwright install
```

## Test Data Cleanup

Tests create data during execution. To clean up:

```bash
# Remove all test data (be careful!)
mongosh nyrkiodb --eval 'db.dropDatabase()'

# Remove test user only
mongosh nyrkiodb --eval 'db.User.deleteOne({email: "test@example.com"})'
```

## CI/CD Considerations

For CI/CD pipelines:

1. Set up MongoDB service
2. Start backend server (wait for health check)
3. Start frontend server (wait for readiness)
4. Create and verify test user
5. Run Playwright tests
6. Clean up test data

Example GitHub Actions:
```yaml
- name: Setup test user
  run: |
    curl -X POST http://localhost:8001/api/v0/auth/register \
      -H "Content-Type: application/json" \
      -d '{"email": "test@example.com", "password": "testpassword123", "username": "testuser"}'
    mongosh nyrkiodb --eval 'db.User.updateOne({email: "test@example.com"}, {$set: {is_verified: true}})'

- name: Run integration tests
  run: npx playwright test --config=playwright.config.integration.ts
```
