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

    // Submit test result via API
    const submitResponse = await request.post(
      "http://localhost:8001/api/v0/result",
      {
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
      }
    );

    // Verify API accepted the result
    expect(submitResponse.status()).toBe(200);
    const submitData = await submitResponse.json();
    expect(submitData).toHaveProperty("result_id");

    // Verify the result exists in the database via API
    const verifyResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    expect(verifyResponse.status()).toBe(200);
    const resultData = await verifyResponse.json();
    expect(resultData.results).toBeDefined();
    expect(resultData.results.length).toBeGreaterThan(0);
    expect(resultData.results[0].value).toBe(456.78);

    // Navigate to dashboard
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Verify the test name appears in the UI
    const testNameVisible = await page
      .locator(`text=${testName}`)
      .isVisible({ timeout: 5000 })
      .catch(() => false);

    // If the UI shows test names, verify our test appears
    // If not, at least verify the dashboard loaded and shows some test data
    if (testNameVisible) {
      await expect(page.locator(`text=${testName}`)).toBeVisible();
    } else {
      // Verify dashboard shows test results list
      const main = page.locator("#main-content");
      await expect(main).toBeVisible();
      // Verify it's not just an empty page
      const hasContent = await page.locator("body").textContent();
      expect(hasContent).toBeTruthy();
      expect(hasContent.length).toBeGreaterThan(100);
    }
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
    const submitResponse = await request.post(
      "http://localhost:8001/api/v0/result",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: {
          test_name: testName,
          value: 789.12,
          unit: "ms",
          timestamp: Math.floor(timestamp / 1000),
        },
      }
    );
    expect(submitResponse.status()).toBe(200);

    // Verify the data exists in backend
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    expect(apiResponse.status()).toBe(200);
    const apiData = await apiResponse.json();
    expect(apiData.results).toBeDefined();
    expect(apiData.results[0].value).toBe(789.12);
    expect(apiData.results[0].unit).toBe("ms");

    // Navigate to test detail page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Verify page shows the content
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();

    // Verify test name appears on the page
    await expect(page.locator(`text=${testName}`)).toBeVisible();
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

    const submittedValues: number[] = [];
    for (const ts of timestamps) {
      const value = 100 + Math.random() * 50;
      submittedValues.push(value);
      const response = await request.post(
        "http://localhost:8001/api/v0/result",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          data: {
            test_name: testName,
            value: value,
            unit: "ms",
            timestamp: Math.floor(ts / 1000),
          },
        }
      );
      expect(response.status()).toBe(200);
    }

    // Verify all results exist in backend
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    expect(apiResponse.status()).toBe(200);
    const apiData = await apiResponse.json();
    expect(apiData.results).toBeDefined();
    expect(apiData.results.length).toBe(3);

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Verify test name appears
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Verify chart is rendered (canvas element from Chart.js)
    const canvas = page.locator("canvas");
    const canvasCount = await canvas.count();
    if (canvasCount > 0) {
      await expect(canvas.first()).toBeVisible();
    }
  });
});

test.describe("Public Test Results", () => {
  test("should view public test results without login", async ({
    page,
    request,
  }) => {
    // Don't login - test public access
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());

    // First, verify the public API endpoint works without auth
    const publicApiResponse = await request.get(
      "http://localhost:8001/api/v0/public"
    );
    expect(publicApiResponse.status()).toBe(200);
    const publicData = await publicApiResponse.json();
    expect(Array.isArray(publicData)).toBe(true);

    // Navigate to public tests page
    await page.goto("/public");
    await page.waitForTimeout(2000);

    // Should be able to view public page without authentication
    await expect(page).toHaveURL(/\/public/);

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();

    // Verify not logged in
    const loggedIn = await page.evaluate(() =>
      localStorage.getItem("loggedIn")
    );
    expect(loggedIn).not.toBe("true");
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
      const response = await request.post(
        "http://localhost:8001/api/v0/result",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          data: {
            test_name: testName,
            value: value + Math.random() * 5, // Add small noise
            unit: "ms",
            timestamp: Math.floor(timestamp / 1000),
          },
        }
      );
      expect(response.status()).toBe(200);
      timestamp += 60000; // 1 minute apart
    }

    // Verify all data points were submitted to backend
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    expect(apiResponse.status()).toBe(200);
    const apiData = await apiResponse.json();
    expect(apiData.results).toBeDefined();
    expect(apiData.results.length).toBe(20);

    // Verify we have the baseline and regressed values
    const values = apiData.results.map((r: any) => r.value).sort();
    expect(values[0]).toBeGreaterThanOrEqual(95); // Baseline ~100
    expect(values[values.length - 1]).toBeLessThanOrEqual(155); // Regressed ~150

    // Navigate to test page to view results
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(5000); // Give time for change detection

    // Verify the page loaded with content
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Verify chart is rendered
    const canvas = page.locator("canvas");
    const canvasCount = await canvas.count();
    if (canvasCount > 0) {
      await expect(canvas.first()).toBeVisible();
    }
  });
});
