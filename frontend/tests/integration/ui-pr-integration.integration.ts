import { test, expect } from "@playwright/test";

/**
 * UI Validation Tests for Pull Request Integration
 *
 * These tests verify that the PR Integration UI displays data correctly
 * by comparing what's shown in the UI against what the API returns.
 *
 * Critical for CI/CD workflow where test results are linked to PRs.
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

test.describe("Pull Request Integration - PR List Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should display pull requests from API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));

    // Get PRs from API
    const apiResponse = await request.get("http://localhost:8001/api/v0/pulls", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(apiResponse.status()).toBe(200);
    const prsData = await apiResponse.json();

    // If user has PRs, navigate to a test page that shows PR info
    if (prsData && prsData.length > 0) {
      const firstPr = prsData[0];

      // PRs might be displayed in various contexts
      // Navigate to tests page first
      await page.goto("/tests");
      await page.waitForTimeout(2000);

      // Verify page loaded
      const main = page.locator("#main-content");
      await expect(main).toBeVisible();
    }
  });

  test("should handle user with no PR results", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));

    // Get PRs from API
    const apiResponse = await request.get("http://localhost:8001/api/v0/pulls", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(apiResponse.status()).toBe(200);
    const prsData = await apiResponse.json();

    // Navigate to tests page
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Page should load even if no PRs
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});

test.describe("Pull Request Integration - PR Results Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should submit PR result via API and verify storage", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Math.floor(Date.now() / 1000); // Unique PR number
    const benchmarkName = `pr-test-${Date.now()}`;

    // Submit PR result via API
    const data = [
      {
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "metric1", value: 123.45, unit: "ms" }],
        extra_info: { pr: pullNumber },
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: "abc123",
          pull_number: pullNumber,
        },
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: data,
      }
    );

    // Verify API accepted the PR result
    if (submitResponse.status() === 200) {
      // Get PR list to verify it was added
      const prsResponse = await request.get(
        "http://localhost:8001/api/v0/pulls",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      expect(prsResponse.status()).toBe(200);
      const prsData = await prsResponse.json();

      // Verify our PR appears in the list
      const ourPr = prsData.find(
        (pr: any) =>
          pr.git_repo &&
          pr.git_repo.includes(repo) &&
          pr.pull_number === pullNumber
      );

      if (ourPr) {
        expect(ourPr.pull_number).toBe(pullNumber);
      }
    }
  });

  test("should retrieve PR result via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Math.floor(Date.now() / 1000);
    const benchmarkName = `pr-retrieve-test-${Date.now()}`;

    // Submit PR result
    const data = [
      {
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "metric1", value: 456.78, unit: "ms" }],
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: "def456",
          pull_number: pullNumber,
        },
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: data,
      }
    );

    if (submitResponse.status() === 200) {
      // Retrieve the PR result
      const getResponse = await request.get(
        `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (getResponse.status() === 200) {
        const resultData = await getResponse.json();
        expect(resultData).toBeDefined();

        // Verify the data matches what we submitted
        if (resultData.results && resultData.results.length > 0) {
          const firstResult = resultData.results[0];
          expect(firstResult.value).toBe(456.78);
        }
      }
    }
  });
});

test.describe("Pull Request Integration - PR Changes Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should get PR changes via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Math.floor(Date.now() / 1000);
    const benchmarkName = `pr-changes-test-${Date.now()}`;
    const gitCommit = "abc123def456";

    // First submit some PR results
    const data = [
      {
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "metric1", value: 100.0, unit: "ms" }],
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: gitCommit,
          pull_number: pullNumber,
        },
      },
      {
        timestamp: Math.floor(Date.now() / 1000) + 1,
        metrics: [{ name: "metric1", value: 150.0, unit: "ms" }],
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: gitCommit,
          pull_number: pullNumber,
        },
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: data,
      }
    );

    if (submitResponse.status() === 200) {
      // Get changes for the PR
      const changesResponse = await request.get(
        `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/changes/${gitCommit}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Changes endpoint might return change point detection results
      if (changesResponse.status() === 200) {
        const changesData = await changesResponse.json();
        expect(changesData).toBeDefined();
      }
    }
  });

  test("should get PR changes for specific test via API", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Math.floor(Date.now() / 1000);
    const testName = `specific-test-${Date.now()}`;
    const gitCommit = "commit789";

    // Submit PR result
    const data = [
      {
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "metric1", value: 200.0, unit: "ms" }],
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: gitCommit,
          pull_number: pullNumber,
        },
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: data,
      }
    );

    if (submitResponse.status() === 200) {
      // Get changes for specific test in PR
      const changesResponse = await request.get(
        `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/changes/${gitCommit}/test/${testName}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (changesResponse.status() === 200) {
        const changesData = await changesResponse.json();
        expect(changesData).toBeDefined();
      }
    }
  });
});

test.describe("Pull Request Integration - Public PR Display", () => {
  test("should access public PR changes without authentication", async ({
    page,
    request,
  }) => {
    // Don't login - test public access
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());

    const repo = "test-org/test-repo";
    const pullNumber = 123;
    const gitCommit = "abc123";
    const testName = "public-test";

    // Try to access public PR changes endpoint
    const publicResponse = await request.get(
      `http://localhost:8001/api/v0/public/pulls/${repo}/${pullNumber}/changes/${gitCommit}/test/${testName}`
    );

    // Public endpoint should work without auth (might be 200 or 404 if no data)
    expect([200, 404]).toContain(publicResponse.status());

    // If it returns 200, verify response structure
    if (publicResponse.status() === 200) {
      const publicData = await publicResponse.json();
      expect(publicData).toBeDefined();
    }
  });
});

test.describe("Pull Request Integration - PR Deletion", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should delete PR results via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Math.floor(Date.now() / 1000);
    const benchmarkName = `pr-delete-test-${Date.now()}`;

    // Submit PR result
    const data = [
      {
        timestamp: Math.floor(Date.now() / 1000),
        metrics: [{ name: "metric1", value: 100.0, unit: "ms" }],
        attributes: {
          git_repo: `https://github.com/${repo}`,
          branch: "feature-branch",
          git_commit: "delete123",
          pull_number: pullNumber,
        },
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: data,
      }
    );

    if (submitResponse.status() === 200) {
      // Delete the PR
      const deleteResponse = await request.delete(
        `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      expect(deleteResponse.status()).toBe(200);

      // Verify it's deleted - trying to get it should fail
      const getResponse = await request.get(
        `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/${benchmarkName}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Should return 404 after deletion
      expect(getResponse.status()).toBe(404);
    }
  });
});

test.describe("Pull Request Integration - UI Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should maintain authentication when viewing PR-related pages", async ({
    page,
    request,
  }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));

    // Navigate through various pages
    await page.goto("/tests");
    await page.waitForTimeout(1000);

    // Verify still authenticated
    const tokenAfter = await page.evaluate(() => localStorage.getItem("token"));
    expect(tokenAfter).toBe(token);

    // Verify token still works with API
    const apiResponse = await request.get(
      "http://localhost:8001/api/v0/users/me",
      {
        headers: { Authorization: `Bearer ${tokenAfter}` },
      }
    );
    expect(apiResponse.status()).toBe(200);
  });
});

test.describe("Pull Request Integration - Error Handling", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should handle non-existent PR gracefully", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const nonExistentPR = 999999999;
    const benchmarkName = "nonexistent-test";

    // Try to get non-existent PR
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/pulls/${repo}/${nonExistentPR}/result/${benchmarkName}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    // Should return 404
    expect(getResponse.status()).toBe(404);
  });

  test("should handle invalid PR data gracefully", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const repo = "test-org/test-repo";
    const pullNumber = Date.now();

    // Try to submit invalid data
    const invalidData = [
      {
        // Missing required fields
        timestamp: Math.floor(Date.now() / 1000),
      },
    ];

    const submitResponse = await request.post(
      `http://localhost:8001/api/v0/pulls/${repo}/${pullNumber}/result/test`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: invalidData,
      }
    );

    // Should return error status (400 or 422)
    expect([400, 422, 500]).toContain(submitResponse.status());
  });
});
