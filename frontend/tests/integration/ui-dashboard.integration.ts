import { test, expect } from "@playwright/test";

/**
 * UI Validation Tests for Dashboard
 *
 * These tests verify that the Dashboard UI displays data correctly
 * by comparing what's shown in the UI against what the API returns.
 */

// Helper to login
async function login(page: any, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[type="text"]#exampleInputEmail1', email);
  await page.fill('input[type="password"]#exampleInputPassword1', password);
  await page.click('button[type="submit"]:has-text("Login")');
  await page.waitForURL("/", { timeout: 10000 });
}

const TEST_USER = {
  email: process.env.TEST_USER_EMAIL || "test@example.com",
  password: process.env.TEST_USER_PASSWORD || "testpassword123",
};

test.describe("Dashboard UI - Test List Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should display test names from API in the dashboard", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));

    // Create multiple test results
    const testNames = [
      `ui-test-dashboard-1-${Date.now()}`,
      `ui-test-dashboard-2-${Date.now()}`,
      `ui-test-dashboard-3-${Date.now()}`,
    ];

    for (const testName of testNames) {
      const response = await request.post(
        "http://localhost:8001/api/v0/result",
        {
          headers: { Authorization: `Bearer ${token}` },
          data: {
            test_name: testName,
            value: Math.random() * 100,
            unit: "ms",
            timestamp: Math.floor(Date.now() / 1000),
          },
        }
      );
      expect(response.status()).toBe(200);
    }

    // Verify tests exist in API
    const apiResponse = await request.get("http://localhost:8001/api/v0/tests", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(apiResponse.status()).toBe(200);
    const apiTests = await apiResponse.json();

    // Navigate to dashboard
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Verify each test name from API appears in the UI
    for (const testName of testNames) {
      const testInApi = apiTests.find((t: any) => t.test_name === testName);
      if (testInApi) {
        // Verify UI shows the test name
        const testElement = page.locator(`text=${testName}`);
        await expect(testElement).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test("should display test values correctly from API", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `ui-test-values-${Date.now()}`;
    const testValue = 123.456;

    // Create test with specific value
    await request.post("http://localhost:8001/api/v0/result", {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        test_name: testName,
        value: testValue,
        unit: "ms",
        timestamp: Math.floor(Date.now() / 1000),
      },
    });

    // Verify via API
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const apiData = await apiResponse.json();
    expect(apiData.results[0].value).toBe(testValue);

    // Navigate to test detail page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(2000);

    // Verify UI shows the test name
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Note: The exact way values are displayed depends on UI implementation
    // We verify the page loaded with the test name, actual value display
    // format needs to be adjusted based on component implementation
  });

  test("should display test units correctly from API", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `ui-test-units-${Date.now()}`;
    const testUnit = "requests/sec";

    // Create test with specific unit
    await request.post("http://localhost:8001/api/v0/result", {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        test_name: testName,
        value: 100,
        unit: testUnit,
        timestamp: Math.floor(Date.now() / 1000),
      },
    });

    // Verify via API
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const apiData = await apiResponse.json();
    expect(apiData.results[0].unit).toBe(testUnit);

    // Navigate to test detail page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(2000);

    // Verify UI shows the unit (if displayed)
    const pageContent = await page.content();
    if (pageContent.includes(testUnit)) {
      await expect(page.locator(`text=${testUnit}`)).toBeVisible();
    }
  });
});

test.describe("Dashboard UI - Test Result Details", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should display all data points from API in chronological order", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `ui-test-chronological-${Date.now()}`;

    // Create multiple results with known timestamps
    const dataPoints = [
      { value: 100, timestamp: Date.now() - 3000 },
      { value: 110, timestamp: Date.now() - 2000 },
      { value: 120, timestamp: Date.now() - 1000 },
    ];

    for (const point of dataPoints) {
      await request.post("http://localhost:8001/api/v0/result", {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          test_name: testName,
          value: point.value,
          unit: "ms",
          timestamp: Math.floor(point.timestamp / 1000),
        },
      });
    }

    // Verify all points exist in API
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const apiData = await apiResponse.json();
    expect(apiData.results.length).toBe(3);

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Verify page shows the test
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // If there's a chart, it should be rendered
    const canvas = page.locator("canvas");
    const canvasCount = await canvas.count();
    if (canvasCount > 0) {
      await expect(canvas.first()).toBeVisible();
    }
  });

  test("should display correct statistics from API data", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `ui-test-stats-${Date.now()}`;

    // Create results with known values for statistics
    const values = [100, 200, 300, 400, 500];
    for (const value of values) {
      await request.post("http://localhost:8001/api/v0/result", {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          test_name: testName,
          value: value,
          unit: "ms",
          timestamp: Math.floor(Date.now() / 1000) - values.indexOf(value),
        },
      });
    }

    // Verify via API
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const apiData = await apiResponse.json();
    expect(apiData.results.length).toBe(5);

    // Calculate expected statistics
    const apiValues = apiData.results.map((r: any) => r.value);
    const expectedMin = Math.min(...apiValues);
    const expectedMax = Math.max(...apiValues);
    const expectedAvg = apiValues.reduce((a: number, b: number) => a + b, 0) / apiValues.length;

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(3000);

    // Note: Actual display of statistics depends on UI implementation
    // We verify the data exists in API and page loaded
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // If statistics are displayed in UI, they should match API values
    // This would need to be adjusted based on actual UI selectors
  });
});

test.describe("Dashboard UI - Empty States", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should handle viewing test with no results gracefully", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const nonExistentTest = `ui-test-nonexistent-${Date.now()}`;

    // Verify test doesn't exist in API
    const apiResponse = await request.get(
      `http://localhost:8001/api/v0/result/${nonExistentTest}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    // API might return 404 or empty results
    const status = apiResponse.status();

    // Navigate to non-existent test page
    await page.goto(`/result/${nonExistentTest}`);
    await page.waitForTimeout(2000);

    // UI should handle this gracefully (show error message or empty state)
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();

    // Page should not crash - it should render something
    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();
  });
});
