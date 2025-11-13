# Nyrkiö Frontend UI Tests

This directory contains end-to-end (E2E) UI tests for the Nyrkiö frontend using Playwright.

## Overview

**Testing Framework:** [Playwright](https://playwright.dev/)
**Test Runner:** `@playwright/test`
**Browser:** Chromium (default)

## Test Types

### Unit Tests (Default)
- Mock API responses
- Fast execution (~1-2s per test)
- Run during development
- Located in: `tests/*.spec.ts`

### Integration Tests
- Use real backend API
- Slower execution (~5-15s per test)
- Run before commits/in CI
- Located in: `tests/integration/*.integration.ts`
- **See:** [Integration Tests README](./integration/README.md)

## Test Files

### `auth.spec.ts` - Authentication Flow Tests

Comprehensive tests for user authentication including:

- **Login Page** - Verifies login page renders correctly with both GitHub OAuth and password options
- **GitHub OAuth Flow** - Tests the complete OAuth flow with GitHub
  - Redirect to GitHub authorization
  - Successful callback handling
  - localStorage population
- **Password Authentication** - Tests email/password login
  - Successful login
  - Failed login with error messages
  - Form validation
- **Session Persistence** - Tests session management
  - localStorage persistence
  - Session across page reloads
- **Logout** - Tests logout functionality
  - localStorage clearing
  - API failure handling
- **UI State Changes** - Tests UI updates based on login state
  - Login button visibility when logged out
  - User menu visibility when logged in

### `logo.spec.ts` - Basic UI Test

Simple test that verifies the Nyrkiö logo renders on the front page.

## Running Tests

### Prerequisites

```bash
# Install dependencies (if not already installed)
npm install

# Install Playwright browsers
npx playwright install chromium
```

### Run Unit Tests (Mocked API)

```bash
# Run all unit tests
npm run test

# Run specific unit test file
npm run test:unit

# Run with UI mode
npm run test-ui
```

### Run Integration Tests (Real API)

**Prerequisites:** MongoDB running, backend configured

```bash
# Run all integration tests
npm run test:integration

# Run with UI mode
npm run test-ui:integration

# View integration test report
npm run test-report:integration
```

**See [Integration Tests README](./integration/README.md) for detailed setup.**

### Run Specific Test File

```bash
npx playwright test tests/auth.spec.ts
```

### Run Tests in UI Mode (Interactive)

```bash
npm run test-ui
```

This opens Playwright's interactive UI where you can:
- See tests running in real-time
- Debug failing tests
- Inspect DOM snapshots
- View network requests

### Run Single Test

```bash
npx playwright test tests/auth.spec.ts -g "should display login page"
```

### Run Tests in Specific Browser

```bash
# Chromium (default)
npx playwright test --project=chromium

# Firefox
npx playwright install firefox
npx playwright test --project=firefox

# WebKit (Safari)
npx playwright install webkit
npx playwright test --project=webkit
```

### Debug Tests

```bash
# Run tests in debug mode
npx playwright test tests/auth.spec.ts --debug

# Run with headed browser (visible)
npx playwright test tests/auth.spec.ts --headed
```

## Test Reports

After running tests, view the HTML report:

```bash
npm run test-report
```

This opens an interactive HTML report showing:
- Test results
- Screenshots on failure
- Execution timeline
- Network activity

## Configuration

Test configuration is in `playwright.config.ts`:

- **Base URL:** `http://127.0.0.1:5173`
- **Web Server:** Automatically starts `npm run dev` before tests
- **Reporters:**
  - List (console output)
  - JSON (machine-readable results)
  - HTML (interactive report)
  - Custom Nyrkiö reporter (sends results to Nyrkiö API)

## Writing New Tests

### Basic Test Structure

```typescript
import { test, expect } from "@playwright/test";

test("test description", async ({ page }) => {
  // Navigate to page
  await page.goto("/path");

  // Interact with elements
  await page.click("button");
  await page.fill("input#email", "test@example.com");

  // Make assertions
  await expect(page.locator("h1")).toHaveText("Expected Text");
});
```

### Test Organization

Group related tests using `test.describe()`:

```typescript
test.describe("Feature Name", () => {
  test("test case 1", async ({ page }) => {
    // ...
  });

  test("test case 2", async ({ page }) => {
    // ...
  });
});
```

### Mocking API Responses

```typescript
test("test with mocked API", async ({ page }) => {
  // Mock API endpoint
  await page.route("/api/v0/some/endpoint", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: "mocked" }),
    });
  });

  await page.goto("/page-that-calls-api");
  // Test continues...
});
```

### Working with localStorage

```typescript
// Set localStorage
await page.evaluate(() => {
  localStorage.setItem("key", "value");
});

// Get localStorage
const value = await page.evaluate(() => localStorage.getItem("key"));

// Clear localStorage
await page.evaluate(() => localStorage.clear());
```

## Best Practices

1. **Use Locators Wisely**
   - Prefer semantic selectors: `page.locator('button:has-text("Login")')`
   - Use data-testid attributes for stable selectors
   - Avoid CSS class selectors that might change

2. **Wait for Elements Properly**
   - Playwright auto-waits, but be explicit when needed
   - Use `await page.waitForSelector()` for dynamic content
   - Use `await page.waitForURL()` after navigations

3. **Isolate Tests**
   - Each test should be independent
   - Clean up state (localStorage, cookies) between tests
   - Don't rely on test execution order

4. **Mock External Dependencies**
   - Mock API calls to avoid flaky tests
   - Don't rely on external services
   - Use realistic mock data

5. **Handle Async Operations**
   - Always `await` async operations
   - Use `page.waitForTimeout()` sparingly (prefer waiting for specific conditions)

## Troubleshooting

### Tests Fail to Start

```bash
# Reinstall dependencies
npm install

# Reinstall Playwright browsers
npx playwright install
```

### Dev Server Won't Start

The config automatically starts `npm run dev`. If this fails:

```bash
# Start dev server manually in another terminal
npm run dev

# Then run tests with existing server
npx playwright test
```

### Tests Timeout

Increase timeout in `playwright.config.ts`:

```typescript
export default defineConfig({
  timeout: 60000, // 60 seconds per test
  // ...
});
```

### Debugging Flaky Tests

```bash
# Run test multiple times
npx playwright test tests/auth.spec.ts --repeat-each=10

# Run with video recording
npx playwright test tests/auth.spec.ts --headed --video=on
```

## CI/CD Integration

Tests are configured to run in CI environments. The config checks `process.env.CI` and adjusts settings accordingly:

- Doesn't reuse existing dev server
- Uses headless mode
- Captures screenshots on failure
- Generates machine-readable reports

## Coverage

### Current Test Coverage

- ✅ Authentication (comprehensive)
- ✅ Logo rendering (basic)
- ⏳ Test results viewing (TODO)
- ⏳ Configuration UI (TODO)
- ⏳ Notifications (TODO)
- ⏳ Organization management (TODO)

### Adding More Tests

Priority areas for additional testing:

1. **Dashboard** - Test results viewing, filtering, charts
2. **Test Configuration** - Settings, notifications, integrations
3. **Organizations** - Team management, billing
4. **Pull Request Integration** - GitHub PR comments
5. **Change Detection** - Viewing and understanding regressions
6. **Responsive Design** - Mobile/tablet layouts
7. **Accessibility** - Keyboard navigation, screen readers

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Testing Library Principles](https://testing-library.com/docs/guiding-principles/)

## Contributing

When adding new tests:

1. Follow existing patterns in `auth.spec.ts`
2. Group tests logically with `test.describe()`
3. Use descriptive test names
4. Add comments for complex test logic
5. Mock external dependencies
6. Ensure tests are isolated and can run independently
7. Update this README if adding new test files or features
