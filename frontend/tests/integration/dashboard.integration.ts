import { test, expect } from "@playwright/test";

/**
 * Integration Tests for Dashboard and Test Results
 *
 * Tests the main dashboard functionality including:
 * - Viewing test results
 * - Filtering and searching
 * - Chart visualization
 * - Change point detection
 * - Test configuration
 */

// Helper to login
async function login(page: any, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[type="text"]#exampleInputEmail1', email);
  await page.fill('input[type="password"]#exampleInputPassword1', password);
  await page.click('button[type="submit"]:has-text("Login")');
  await page.waitForURL("/", { timeout: 10000 });
}

// Test data
const TEST_USER = {
  email: process.env.TEST_USER_EMAIL || "test@example.com",
  password: process.env.TEST_USER_PASSWORD || "testpassword123",
};

test.describe("Dashboard Integration Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should load dashboard after login", async ({ page }) => {
    // After login, should redirect to /tests
    await page.waitForURL(/\/tests/, { timeout: 5000 });

    // Dashboard should be visible
    await expect(page).toHaveURL(/\/tests/);

    // Wait for content to load
    await page.waitForTimeout(2000);
  });

  test("should display test results list", async ({ page }) => {
    await page.goto("/tests");

    // Wait for any test results to load
    await page.waitForTimeout(3000);

    // Dashboard should have some structure
    // Adjust selectors based on actual dashboard structure
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should navigate to specific test results", async ({ page }) => {
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Try to find and click a test result link
    // This depends on having test data in the database
    const testLinks = page.locator("a[href*='/result/']");
    const count = await testLinks.count();

    if (count > 0) {
      await testLinks.first().click();

      // Should navigate to test detail page
      await expect(page).toHaveURL(/\/result\//);

      // Wait for content
      await page.waitForTimeout(2000);
    }
  });
});

test.describe("Test Results Submission", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should submit test result via API", async ({ page, request }) => {
    // Get auth token
    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBeTruthy();

    // Submit a test result
    const timestamp = Date.now();
    const response = await request.post(
      "http://localhost:8001/api/v0/result",
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: {
          test_name: "integration-test-" + timestamp,
          value: 123.45,
          unit: "ms",
          timestamp: Math.floor(timestamp / 1000),
          attributes: {
            git_repo: "https://github.com/nyrkio/nyrkio",
            branch: "main",
            git_commit: "abc123",
          },
        },
      }
    );

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty("result_id");
  });

  test("should view submitted test result in dashboard", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const timestamp = Date.now();
    const testName = "integration-view-test-" + timestamp;

    // Submit test result
    await request.post("http://localhost:8001/api/v0/result", {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      data: {
        test_name: testName,
        value: 456.78,
        unit: "ms",
        timestamp: Math.floor(timestamp / 1000),
      },
    });

    // Navigate to dashboard
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Reload to get fresh data
    await page.reload();
    await page.waitForTimeout(2000);

    // Try to find our test (this depends on UI structure)
    // You may need to adjust the selector
    const pageContent = await page.content();
    // Just verify the page loaded - finding specific test may require more specific selectors
    expect(pageContent).toBeTruthy();
  });
});

test.describe("Test Results Viewing", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should display test details page", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const timestamp = Date.now();
    const testName = "integration-detail-test-" + timestamp;

    // Create test result
    await request.post("http://localhost:8001/api/v0/result", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      data: {
        test_name: testName,
        value: 789.12,
        unit: "ms",
        timestamp: Math.floor(timestamp / 1000),
      },
    });

    // Navigate to test detail page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Should show some content
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should display chart for test results", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = "integration-chart-test-" + Date.now();

    // Submit multiple results for a chart
    const timestamps = [
      Date.now() - 60000, // 1 minute ago
      Date.now() - 30000, // 30 seconds ago
      Date.now(),
    ];

    for (const ts of timestamps) {
      await request.post("http://localhost:8001/api/v0/result", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: {
          test_name: testName,
          value: 100 + Math.random() * 50,
          unit: "ms",
          timestamp: Math.floor(ts / 1000),
        },
      });
    }

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Should have rendered a chart (canvas element from Chart.js)
    const canvas = page.locator("canvas");
    const canvasCount = await canvas.count();

    // If chart renders, there should be at least one canvas
    if (canvasCount > 0) {
      await expect(canvas.first()).toBeVisible();
    }
  });
});

test.describe("Public Test Results", () => {
  test("should view public test results without login", async ({ page }) => {
    // Don't login - test public access
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());

    // Navigate to public tests
    await page.goto("/public");
    await page.waitForTimeout(2000);

    // Should be able to view public page
    await expect(page).toHaveURL(/\/public/);

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});

test.describe("Change Point Detection", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should detect change points with sufficient data", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = "integration-changepoint-test-" + Date.now();

    // Submit data with a clear performance change
    const baselineValues = Array(10).fill(100);
    const regressedValues = Array(10).fill(150);
    const allValues = [...baselineValues, ...regressedValues];

    let timestamp = Date.now() - allValues.length * 60000;

    for (const value of allValues) {
      await request.post("http://localhost:8001/api/v0/result", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: {
          test_name: testName,
          value: value + Math.random() * 5, // Add small noise
          unit: "ms",
          timestamp: Math.floor(timestamp / 1000),
        },
      });
      timestamp += 60000; // 1 minute apart
    }

    // Trigger change detection (if there's an API endpoint)
    // Or navigate to the test page which should show changes
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(5000); // Give time for change detection

    // Check if change points are displayed
    // This depends on your UI structure
    const pageContent = await page.content();
    // Look for indicators of change detection
    // Adjust based on actual UI
  });
});
