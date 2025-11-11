# Integration Tests

Integration tests that run against the real Nyrkiö backend API.

## Overview

Unlike unit tests which mock the API, integration tests:
- ✅ Start a real backend server (`http://localhost:8001`)
- ✅ Start a real frontend dev server (`http://localhost:5173`)
- ✅ Test actual API endpoints
- ✅ Verify real database interactions
- ✅ Test complete end-to-end workflows

## Prerequisites

### 1. MongoDB Running

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use Docker Compose
python3 ../../etc/nyrkio_docker.py start

# Or install MongoDB locally
# See: https://docs.mongodb.com/manual/installation/
```

### 2. Backend Configuration

Create/update `.env.backend` in the project root:

```bash
# Minimum required for integration tests
DB_URL=mongodb://localhost:27017/nyrkiodb_test
DB_NAME=nyrkiodb_test
SECRET_KEY=test_secret_key_for_integration_tests
API_PORT=8001
```

**Important:** Use a separate test database to avoid affecting production/development data!

### 3. Backend Dependencies

```bash
cd backend
poetry install
cd ..
```

### 4. Test User Setup

Integration tests require a test user account. You have two options:

**Option A: Set environment variables**

```bash
export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="testpassword123"
export TEST_USER_USERNAME="testuser"
```

**Option B: Create test user manually**

Use the backend API or MongoDB directly to create a test user before running tests.

### 5. Frontend Dependencies

```bash
cd frontend
npm install
npx playwright install chromium
cd ..
```

## Running Integration Tests

### Run All Integration Tests

```bash
cd frontend
npx playwright test --config=playwright.config.integration.ts
```

### Run Specific Test File

```bash
npx playwright test tests/integration/auth.integration.ts --config=playwright.config.integration.ts
```

### Run in UI Mode (Interactive)

```bash
npx playwright test --config=playwright.config.integration.ts --ui
```

### Run with Visible Browser (Headed)

```bash
npx playwright test --config=playwright.config.integration.ts --headed
```

### Debug Mode

```bash
npx playwright test --config=playwright.config.integration.ts --debug
```

### Run Single Test

```bash
npx playwright test --config=playwright.config.integration.ts -g "should successfully login"
```

## Configuration

Integration tests use `playwright.config.integration.ts` which:

- **Starts backend automatically** using `python3 ../etc/nyrkio_backend.py start`
- **Starts frontend automatically** using `npm run dev`
- **Runs tests serially** (workers: 1) to avoid conflicts
- **Longer timeouts** (60s per test) for real API calls
- **Records traces/videos** on failure for debugging

## Test Structure

### `auth.integration.ts`

Complete authentication flow tests:

- **Login Page**: Loads correctly with real backend
- **Password Authentication**:
  - Successful login with valid credentials
  - Error messages with invalid credentials
  - Form validation
- **Session Persistence**:
  - Across page navigation
  - Across page reload
- **Logout**: Complete logout flow
- **Protected Routes**: Access control verification
- **API Token Usage**: JWT token in requests
- **GitHub OAuth**: OAuth flow initiation

## Writing Integration Tests

### Basic Structure

```typescript
import { test, expect } from "@playwright/test";

test.describe("Feature Name Integration", () => {
  test.beforeEach(async ({ page }) => {
    // Clean up before each test
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
  });

  test("should do something with real API", async ({ page }) => {
    await page.goto("/some-page");

    // Interact with UI
    await page.fill("input", "value");
    await page.click("button");

    // Real API request happens here
    await page.waitForResponse((response) =>
      response.url().includes("/api/")
    );

    // Verify result
    await expect(page.locator(".result")).toBeVisible();
  });
});
```

### Best Practices

1. **Clean State**: Always clear localStorage and reset state between tests
2. **Wait for API**: Use `page.waitForResponse()` for API calls
3. **Longer Timeouts**: Real APIs are slower, use appropriate timeouts
4. **Separate Database**: Use a test database, not production
5. **Idempotent Tests**: Tests should be repeatable without manual cleanup
6. **Serial Execution**: Run tests serially to avoid database conflicts

### Monitoring API Calls

```typescript
test("verify API behavior", async ({ page }) => {
  // Listen for specific API call
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes("/api/v0/result")
  );

  // Trigger the call
  await page.click("button.fetch-data");

  // Wait and verify
  const response = await responsePromise;
  expect(response.status()).toBe(200);

  const data = await response.json();
  expect(data).toHaveProperty("results");
});
```

### Testing with Real Data

```typescript
test("create and verify data", async ({ page, request }) => {
  // Get auth token
  await page.goto("/login");
  // ... login flow ...
  const token = await page.evaluate(() => localStorage.getItem("token"));

  // Create test data via API
  await request.post("http://localhost:8001/api/v0/result", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    data: {
      test_name: "integration-test",
      value: 123,
    },
  });

  // Navigate and verify UI shows the data
  await page.goto("/dashboard");
  await expect(page.locator("text=integration-test")).toBeVisible();
});
```

## Troubleshooting

### Backend Won't Start

```bash
# Check if backend is already running
python3 ../etc/nyrkio_backend.py status

# Stop any existing backend
python3 ../etc/nyrkio_backend.py stop

# Check MongoDB is running
docker ps | grep mongodb

# Check .env.backend exists
ls -la ../.env.backend

# Try starting manually
python3 ../etc/nyrkio_backend.py start
curl http://localhost:8001/docs
```

### Tests Timeout

- **Increase timeout** in `playwright.config.integration.ts`
- **Check API logs** - backend might be slow or hanging
- **Check database** - might be slow to respond
- **Network issues** - verify localhost connectivity

### Database State Issues

```bash
# Clear test database between runs
mongo nyrkiodb_test --eval "db.dropDatabase()"

# Or use a script to reset state
python3 scripts/reset_test_db.py
```

### Port Conflicts

```bash
# Check if ports are in use
lsof -i :8001  # Backend
lsof -i :5173  # Frontend

# Kill processes if needed
kill -9 <PID>
```

### Tests Fail but UI Works Manually

- Check **timing issues** - add explicit waits
- Check **state cleanup** - localStorage/cookies might persist
- Check **test data** - might conflict with existing data
- Run in **headed mode** to see what's happening

## CI/CD Integration

Integration tests in CI require:

1. **MongoDB container** running
2. **Test database** configured
3. **Test user** created
4. **Environment variables** set

Example GitHub Actions:

```yaml
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: |
          cd backend && poetry install && cd ..
          cd frontend && npm install && cd ..

      - name: Setup test database
        run: python3 scripts/setup_test_db.py

      - name: Run integration tests
        run: |
          cd frontend
          npx playwright install chromium
          npx playwright test --config=playwright.config.integration.ts
        env:
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}
```

## Performance

Integration tests are slower than unit tests:

- **Unit tests**: ~1-2 seconds per test
- **Integration tests**: ~5-15 seconds per test

Run integration tests:
- ✅ Before committing major changes
- ✅ In CI/CD pipeline
- ✅ When API contracts change
- ❌ Not constantly during development (use unit tests)

## Coverage

Current integration test coverage:

- ✅ Authentication flow (comprehensive)
- ⏳ Dashboard and results viewing (TODO)
- ⏳ Test configuration (TODO)
- ⏳ Organization management (TODO)
- ⏳ Notifications (TODO)
- ⏳ Pull request integration (TODO)

## Comparison: Unit vs Integration Tests

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| **Speed** | Fast (~1-2s) | Slow (~5-15s) |
| **Backend** | Mocked | Real |
| **Database** | None | Real MongoDB |
| **Isolation** | Complete | Shared state |
| **Reliability** | Very reliable | Can be flaky |
| **Debugging** | Easy | Harder |
| **Coverage** | UI/Frontend only | Full stack |
| **When to use** | Development | Pre-commit, CI |

## Related Documentation

- Unit tests: `../README.md`
- Backend API: `../../backend/README.md`
- Management scripts: `../../etc/README.md`
- Playwright docs: https://playwright.dev/
