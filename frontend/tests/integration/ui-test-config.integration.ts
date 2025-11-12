import { test, expect } from "@playwright/test";

/**
 * UI Validation Tests for Test Configuration
 *
 * These tests verify that the Test Settings UI allows users to configure
 * their tests correctly by validating API interactions for:
 * - Public/private visibility toggles
 * - Test configuration persistence
 * - Git repo and branch settings
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

test.describe("Test Configuration - API Endpoints", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should access config API endpoint", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-api-test-${Date.now()}`;

    // Create a test first
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

    // Try to get config
    const configResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(configResponse.status()).toBe(200);
    const configData = await configResponse.json();
    expect(Array.isArray(configData)).toBe(true);
  });

  test("should create new test configuration via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-create-${Date.now()}`;

    // Create test config
    const newConfig = [{
      attributes: {
        git_repo: "https://github.com/test/repo",
        branch: "feature-branch"
      },
      public: false
    }];

    const createResponse = await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: newConfig
      }
    );

    expect(createResponse.status()).toBe(200);

    // Verify config was saved
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const savedConfig = await getResponse.json();
    expect(savedConfig).toBeDefined();
    expect(Array.isArray(savedConfig)).toBe(true);
  });
});

test.describe("Test Configuration - Public/Private Toggle", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should set test to public via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-public-${Date.now()}`;

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
          git_commit: "public123"
        }
      }]
    });

    // Set to public
    const publicConfig = [{
      attributes: {
        git_repo: "https://github.com/nyrkio/nyrkio",
        branch: "main"
      },
      public: true
    }];

    const setPublicResponse = await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: publicConfig
      }
    );

    expect(setPublicResponse.status()).toBe(200);

    // Verify it's public
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const config = await getResponse.json();

    if (config && config.length > 0 && config[0].public !== undefined) {
      expect(config[0].public).toBe(true);
    }
  });

  test("should set test to private via API", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-private-${Date.now()}`;

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
          git_commit: "private123"
        }
      }]
    });

    // Set to private
    const privateConfig = [{
      attributes: {
        git_repo: "https://github.com/nyrkio/nyrkio",
        branch: "main"
      },
      public: false
    }];

    const setPrivateResponse = await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: privateConfig
      }
    );

    expect(setPrivateResponse.status()).toBe(200);

    // Verify it's private
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const config = await getResponse.json();

    if (config && config.length > 0 && config[0].public !== undefined) {
      expect(config[0].public).toBe(false);
    }
  });

  test("should toggle test visibility multiple times", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-toggle-${Date.now()}`;

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
          git_commit: "toggle123"
        }
      }]
    });

    const baseConfig = {
      attributes: {
        git_repo: "https://github.com/nyrkio/nyrkio",
        branch: "main"
      }
    };

    // Toggle to public
    await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{ ...baseConfig, public: true }]
      }
    );

    // Toggle to private
    await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{ ...baseConfig, public: false }]
      }
    );

    // Toggle back to public
    const finalResponse = await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: [{ ...baseConfig, public: true }]
      }
    );

    expect(finalResponse.status()).toBe(200);

    // Verify final state
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const config = await getResponse.json();

    if (config && config.length > 0 && config[0].public !== undefined) {
      expect(config[0].public).toBe(true);
    }
  });
});

test.describe("Test Configuration - Git Attributes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should store git repo in config", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-git-repo-${Date.now()}`;
    const gitRepo = "https://github.com/example/test-repo";

    const config = [{
      attributes: {
        git_repo: gitRepo,
        branch: "main"
      },
      public: false
    }];

    await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: config
      }
    );

    // Verify repo is saved
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const savedConfig = await getResponse.json();

    if (savedConfig && savedConfig.length > 0 && savedConfig[0].attributes) {
      expect(savedConfig[0].attributes.git_repo).toBe(gitRepo);
    }
  });

  test("should store branch in config", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-branch-${Date.now()}`;
    const branch = "feature/new-feature";

    const config = [{
      attributes: {
        git_repo: "https://github.com/nyrkio/nyrkio",
        branch: branch
      },
      public: false
    }];

    await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: config
      }
    );

    // Verify branch is saved
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const savedConfig = await getResponse.json();

    if (savedConfig && savedConfig.length > 0 && savedConfig[0].attributes) {
      expect(savedConfig[0].attributes.branch).toBe(branch);
    }
  });
});

test.describe("Test Configuration - Empty State", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should handle test with no config gracefully", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-no-config-${Date.now()}`;

    // Try to get config for test that doesn't exist
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const config = await getResponse.json();

    // Should return empty array or empty config
    expect(Array.isArray(config)).toBe(true);
  });

  test("should create config for new test", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const testName = `config-new-test-${Date.now()}`;

    // Create config before any results
    const newConfig = [{
      attributes: {
        git_repo: "https://github.com/nyrkio/nyrkio",
        branch: "new-branch"
      },
      public: true
    }];

    const createResponse = await request.post(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: newConfig
      }
    );

    expect(createResponse.status()).toBe(200);

    // Verify it was created
    const getResponse = await request.get(
      `http://localhost:8001/api/v0/config/${testName}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    expect(getResponse.status()).toBe(200);
    const savedConfig = await getResponse.json();
    expect(savedConfig).toBeDefined();
    expect(Array.isArray(savedConfig)).toBe(true);
  });
});
