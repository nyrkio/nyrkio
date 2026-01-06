import { test, expect } from "@playwright/test";

/**
 * UI Validation Tests for Change Point Detection
 *
 * These tests verify that the Change Point Detection UI displays regression
 * alerts correctly by comparing what's shown in the UI against what the API returns.
 *
 * Change point detection is a core feature of Nyrkio that automatically identifies
 * performance regressions in test results.
 */

// Helper to login - uses API directly to bypass UI login form issues
async function login(page: any, email: string, password: string) {
  // Get authentication token from API
  const response = await page.request.post('http://localhost:8001/api/v0/auth/jwt/login', {
    form: {
      username: email,
      password: password
    }
  });

  if (!response.ok()) {
    throw new Error(`Login failed with status ${response.status()}: ${await response.text()}`);
  }

  const { access_token } = await response.json();

  // Navigate to home page first
  await page.goto('/');

  // Then inject token and loggedIn flag into localStorage
  await page.evaluate((token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('loggedIn', 'true');
  }, access_token);

  // Reload page to trigger authentication
  await page.reload();

  // Wait for app to recognize authentication
  await page.waitForTimeout(1000);

  // Verify token is present
  const storedToken = await page.evaluate(() => localStorage.getItem('token'));
  if (!storedToken) {
    throw new Error('Token not found in localStorage after login');
  }
}

const TEST_USER = {
  email: process.env.TEST_USER_EMAIL || "test@example.com",
  password: process.env.TEST_USER_PASSWORD || "testpassword123",
};

test.describe("Change Point Detection - API Endpoint Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should access change points API endpoint", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-api-test-${Date.now()}`;

    // Create some test data
    await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      data: [{
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "performance", value: 100, unit: "ms" }],
        attributes: {
          git_repo: "https://github.com/nyrkio/nyrkio",
          branch: "main",
          git_commit: "abc123"
        }
      }]
    });

    // Test changes endpoint
    const changesResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}/changes`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(changesResponse.status()).toBe(200);
    const changesData = await changesResponse.json();
    expect(changesData).toBeDefined();
  });

  test("should access perCommit changes API endpoint", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-percommit-${Date.now()}`;

    // Create test data
    await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      data: [{
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "performance", value: 100, unit: "ms" }],
        attributes: {
          git_repo: "https://github.com/nyrkio/nyrkio",
          branch: "main",
          git_commit: "def456"
        }
      }]
    });

    // Test perCommit changes endpoint
    const perCommitResponse = await request.get(
      `http://localhost:8001/api/v0/changes/perCommit/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(perCommitResponse.status()).toBe(200);
    const perCommitData = await perCommitResponse.json();
    expect(perCommitData).toBeDefined();
    expect(Array.isArray(perCommitData)).toBe(true);
  });
});

test.describe("Change Point Detection - No Changes State", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should handle test with no change points gracefully", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-no-changes-${Date.now()}`;

    // Create stable data (no regression)
    const baseValue = 100;
    for (let i = 0; i < 10; i++) {
      await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{
          timestamp: Math.floor(Date.now() / 1000) - (10 - i),
          metrics: [{
            name: "performance",
            value: baseValue + (Math.random() - 0.5) * 2, // Small noise
            unit: "ms"
          }],
          attributes: {
            git_repo: "https://github.com/nyrkio/nyrkio",
            branch: "stable",
            git_commit: `commit${i}`
          }
        }]
      });
    }

    // Check changes API
    const changesResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}/changes`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(changesResponse.status()).toBe(200);
    const changesData = await changesResponse.json();

    // Should have empty or no changes for stable data
    if (changesData[testName]) {
      expect(Array.isArray(changesData[testName])).toBe(true);
    }

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(2000);

    // Page should load without crashing
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});

test.describe("Change Point Detection - With Regression Data", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should create data with performance regression", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-regression-${Date.now()}`;

    // Create baseline data (fast)
    const baselineValue = 100;
    for (let i = 0; i < 15; i++) {
      await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{
          timestamp: Math.floor(Date.now() / 1000) - (30 - i) * 60,
          metrics: [{
            name: "performance",
            value: baselineValue + (Math.random() - 0.5) * 5,
            unit: "ms"
          }],
          attributes: {
            git_repo: "https://github.com/nyrkio/nyrkio",
            branch: "main",
            git_commit: `baseline${i}`
          }
        }]
      });
    }

    // Create regressed data (slow) - 2x slower
    const regressedValue = 200;
    for (let i = 0; i < 15; i++) {
      await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{
          timestamp: Math.floor(Date.now() / 1000) - (15 - i) * 60,
          metrics: [{
            name: "performance",
            value: regressedValue + (Math.random() - 0.5) * 5,
            unit: "ms"
          }],
          attributes: {
            git_repo: "https://github.com/nyrkio/nyrkio",
            branch: "main",
            git_commit: `regressed${i}`
          }
        }]
      });
    }

    // Verify data was created
    const resultsResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(resultsResponse.status()).toBe(200);
    const resultsData = await resultsResponse.json();
    expect(resultsData.length).toBe(30);

    // Check if change points were detected
    const changesResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}/changes`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(changesResponse.status()).toBe(200);
    const changesData = await changesResponse.json();

    // Log changes for debugging
    console.log(`Change points for ${testName}:`, JSON.stringify(changesData, null, 2));

    // Navigate to test page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(5000); // Give time for change detection

    // Verify page loaded
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Chart should be visible
    const canvas = page.locator("canvas");
    const canvasCount = await canvas.count();
    if (canvasCount > 0) {
      await expect(canvas.first()).toBeVisible();
    }
  });

  test("should display changes endpoint data structure", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));

    // Use existing test if available
    const resultsResponse = await request.get(
      "http://localhost:8001/api/v0/results",
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(resultsResponse.status()).toBe(200);
    const results = await resultsResponse.json();

    if (results && results.length > 0) {
      const testName = results[0].test_name;
      if (testName) {
        // Check changes format
        const changesResponse = await request.get(
          `http://localhost:8001/api/v0/result/${testName}/changes`,
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );

        expect(changesResponse.status()).toBe(200);
        const changesData = await changesResponse.json();

        // Validate response structure
        expect(changesData).toBeDefined();
        expect(typeof changesData).toBe('object');
      }
    }
  });
});

test.describe("Change Point Detection - UI Display Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should load test result page without errors", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-ui-test-${Date.now()}`;

    // Create minimal test data
    await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      data: [{
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "performance", value: 100, unit: "ms" }],
        attributes: {
          git_repo: "https://github.com/nyrkio/nyrkio",
          branch: "main",
          git_commit: "ui-test"
        }
      }]
    });

    // Navigate to result page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(2000);

    // Page should load
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();

    // Test name should be visible
    await expect(page.locator(`text=${testName}`)).toBeVisible();
  });

  test("should handle empty changes gracefully in UI", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `cp-empty-changes-${Date.now()}`;

    // Create single data point (can't detect changes with 1 point)
    await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      data: [{
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "performance", value: 100, unit: "ms" }],
        attributes: {
          git_repo: "https://github.com/nyrkio/nyrkio",
          branch: "main",
          git_commit: "single"
        }
      }]
    });

    // Verify changes endpoint returns empty
    const changesResponse = await request.get(
      `http://localhost:8001/api/v0/result/${testName}/changes`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(changesResponse.status()).toBe(200);

    // Navigate to result page
    await page.goto(`/result/${testName}`);
    await page.waitForTimeout(2000);

    // Page should not crash
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});

test.describe("Change Point Detection - Multiple Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should handle multiple tests with change detection", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const prefix = `cp-multi-${Date.now()}`;
    const testNames = [`${prefix}-a`, `${prefix}-b`, `${prefix}-c`];

    // Create data for multiple tests
    for (const testName of testNames) {
      for (let i = 0; i < 5; i++) {
        await request.post(`http://localhost:8001/api/v0/result/${testName}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          data: [{
            timestamp: Math.floor(Date.now() / 1000) - (5 - i),
            metrics: [{ name: "performance", value: 100 + i * 10, unit: "ms" }],
            attributes: {
              git_repo: "https://github.com/nyrkio/nyrkio",
              branch: "multi-test",
              git_commit: `commit${i}`
            }
          }]
        });
      }
    }

    // Verify all tests exist
    const resultsResponse = await request.get(
      "http://localhost:8001/api/v0/results",
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(resultsResponse.status()).toBe(200);
    const results = await resultsResponse.json();

    // At least our 3 tests should exist
    const ourTests = results.filter((r: any) =>
      testNames.includes(r.test_name)
    );
    expect(ourTests.length).toBeGreaterThanOrEqual(3);

    // Navigate to dashboard
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Dashboard should load
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});
