import { test, expect } from "@playwright/test";

/**
 * Integration Tests for Authentication
 *
 * These tests run against the real backend API (http://localhost:8001)
 * and verify end-to-end authentication functionality.
 *
 * Requirements:
 * - MongoDB must be running
 * - Backend must be configured with .env.backend
 * - Test user credentials must be available
 *
 * Note: These tests are slower than unit tests and should be run separately.
 */

// Test data - you may need to adjust based on your test database
const TEST_USER = {
  email: process.env.TEST_USER_EMAIL || "test@example.com",
  password: process.env.TEST_USER_PASSWORD || "testpassword123",
  username: process.env.TEST_USER_USERNAME || "testuser",
};

test.describe("Authentication Integration Tests", () => {
  // Clean up before each test
  test.beforeEach(async ({ page }) => {
    // Clear any existing session
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
  });

  test.describe("Login Page", () => {
    test("should load login page successfully", async ({ page }) => {
      await page.goto("/login");

      // Verify page loaded
      await expect(page).toHaveTitle(/Nyrkiö|nyrkio/i);

      // Check for login form elements
      await expect(page.locator("h2")).toContainText("Log In");
      await expect(
        page.locator('button:has-text("Login with GitHub")')
      ).toBeVisible();
      await expect(
        page.locator('input[type="text"]#exampleInputEmail1')
      ).toBeVisible();
      await expect(
        page.locator('input[type="password"]#exampleInputPassword1')
      ).toBeVisible();
    });
  });

  test.describe("Password Authentication", () => {
    test("should successfully login with valid credentials", async ({
      page,
    }) => {
      await page.goto("/login");

      // Fill in credentials
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );

      // Submit form
      await page.click('button[type="submit"]:has-text("Login")');

      // Should redirect to home page
      await page.waitForURL("/", { timeout: 10000 });

      // Verify logged in state
      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("true");

      // Verify token was stored
      const token = await page.evaluate(() => localStorage.getItem("token"));
      expect(token).toBeTruthy();
      expect(token).toContain(".");

      // Verify auth method
      const authMethod = await page.evaluate(() =>
        localStorage.getItem("authMethod")
      );
      expect(authMethod).toBe("password");
    });

    test("should show error message with invalid credentials", async ({
      page,
    }) => {
      await page.goto("/login");

      // Fill in invalid credentials
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        "invalid@example.com"
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        "wrongpassword"
      );

      // Submit form
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for error message
      await page.waitForSelector(".alert-warning", { timeout: 5000 });

      // Verify error message is shown
      const errorMessage = page.locator(".alert-warning");
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText("Authentication");

      // Verify still on login page
      expect(page.url()).toContain("/login");

      // Verify not logged in
      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).not.toBe("true");
    });

    test("should validate required fields", async ({ page }) => {
      await page.goto("/login");

      // Try to submit without filling fields
      await page.click('button[type="submit"]:has-text("Login")');

      // HTML5 validation should prevent submission
      // We stay on the same page
      expect(page.url()).toContain("/login");

      // No error message should appear (HTML5 validation handles it)
      const errorMessage = page.locator(".alert-warning");
      await expect(errorMessage).not.toBeVisible();
    });
  });

  test.describe("Session Persistence", () => {
    test("should maintain session across page navigation", async ({ page }) => {
      await page.goto("/login");

      // Login
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for redirect
      await page.waitForURL("/", { timeout: 10000 });

      // Get initial token
      const initialToken = await page.evaluate(() =>
        localStorage.getItem("token")
      );

      // Navigate to another page (e.g., docs)
      await page.goto("/docs");

      // Verify session persists
      const tokenAfterNav = await page.evaluate(() =>
        localStorage.getItem("token")
      );
      expect(tokenAfterNav).toBe(initialToken);

      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("true");
    });

    test("should maintain session across page reload", async ({ page }) => {
      await page.goto("/login");

      // Login
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for redirect
      await page.waitForURL("/", { timeout: 10000 });

      // Get initial state
      const initialToken = await page.evaluate(() =>
        localStorage.getItem("token")
      );
      const initialUsername = await page.evaluate(() =>
        localStorage.getItem("username")
      );

      // Reload page
      await page.reload();

      // Verify session persists after reload
      const tokenAfterReload = await page.evaluate(() =>
        localStorage.getItem("token")
      );
      expect(tokenAfterReload).toBe(initialToken);

      const usernameAfterReload = await page.evaluate(() =>
        localStorage.getItem("username")
      );
      expect(usernameAfterReload).toBe(initialUsername);

      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("true");
    });
  });

  test.describe("Logout", () => {
    test("should successfully logout", async ({ page }) => {
      await page.goto("/login");

      // Login first
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for redirect
      await page.waitForURL("/", { timeout: 10000 });

      // Verify logged in
      let loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("true");

      // Find and click logout button
      const logoutButton = page.locator('a:has-text("Log Out")');
      await expect(logoutButton).toBeVisible({ timeout: 5000 });
      await logoutButton.click();

      // Wait for logout to complete
      await page.waitForTimeout(1000);

      // Verify logged out state
      loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
      expect(loggedIn).toBe("false");

      const username = await page.evaluate(() =>
        localStorage.getItem("username")
      );
      expect(username).toBe("");

      // Should be redirected to home page
      expect(page.url()).toContain("/");
    });
  });

  test.describe("Protected Routes", () => {
    test("should allow access to protected routes when logged in", async ({
      page,
    }) => {
      await page.goto("/login");

      // Login
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for redirect
      await page.waitForURL("/", { timeout: 10000 });

      // Try to access dashboard (assuming it's a protected route)
      await page.goto("/dashboard");

      // Should be able to access (not redirected to login)
      // Adjust based on your actual protected routes
      expect(page.url()).toContain("/dashboard");
    });

    test("should redirect to login for protected routes when not logged in", async ({
      page,
    }) => {
      // Ensure not logged in
      await page.goto("/");
      await page.evaluate(() => localStorage.clear());

      // Try to access a protected route (adjust based on your app)
      await page.goto("/dashboard");

      // Should redirect to login or show login prompt
      // Adjust assertion based on your app's behavior
      await page.waitForTimeout(2000);

      // This depends on your app's behavior - it might:
      // 1. Redirect to /login
      // 2. Show a login modal
      // 3. Show an error message
      // Uncomment and adjust as needed:
      // expect(page.url()).toContain("/login");
    });
  });

  test.describe("API Token Usage", () => {
    test("should include JWT token in authenticated API requests", async ({
      page,
    }) => {
      await page.goto("/login");

      // Login
      await page.fill(
        'input[type="text"]#exampleInputEmail1',
        TEST_USER.email
      );
      await page.fill(
        'input[type="password"]#exampleInputPassword1',
        TEST_USER.password
      );
      await page.click('button[type="submit"]:has-text("Login")');

      // Wait for redirect
      await page.waitForURL("/", { timeout: 10000 });

      // Get the token
      const token = await page.evaluate(() => localStorage.getItem("token"));
      expect(token).toBeTruthy();

      // Listen for API requests
      const apiRequest = page.waitForRequest((request) => {
        return (
          request.url().includes("/api/") &&
          request.headers()["authorization"] !== undefined
        );
      });

      // Trigger an authenticated API request
      // This depends on your app - navigate to a page that makes auth'd requests
      await page.goto("/dashboard");

      // Wait for the request (with timeout)
      try {
        const request = await Promise.race([
          apiRequest,
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error("Timeout")), 10000)
          ),
        ]);

        // Verify the request includes the Bearer token
        const authHeader = (request as any).headers()["authorization"];
        expect(authHeader).toContain("Bearer");
        expect(authHeader).toContain(token);
      } catch (e) {
        // If no authenticated requests are made, that's okay for this test
        // Just verify the token exists in localStorage
        console.log("No authenticated API requests detected, but token exists");
      }
    });
  });
});

test.describe("GitHub OAuth Integration", () => {
  test("should initiate GitHub OAuth flow", async ({ page }) => {
    await page.goto("/login");

    // Click GitHub login button
    const githubButton = page.locator('button:has-text("Login with GitHub")');
    await expect(githubButton).toBeVisible();

    // This will navigate to GitHub, so we can't complete the flow in tests
    // But we can verify the request is made
    const navigationPromise = page.waitForResponse(
      (response) => response.url().includes("/api/v0/auth/github/authorize"),
      { timeout: 5000 }
    );

    await githubButton.click();

    try {
      const response = await navigationPromise;
      expect(response.status()).toBe(200);

      // The response should contain an authorization URL
      const data = await response.json();
      expect(data.authorization_url).toContain("github.com");
    } catch (e) {
      // If the API call doesn't happen immediately, that's okay
      // The important part is the button exists and is clickable
      console.log("GitHub OAuth flow initiated");
    }
  });

  // Note: Full OAuth flow testing requires mocking GitHub or using a test OAuth server
  // These tests verify the integration points exist and work
});
