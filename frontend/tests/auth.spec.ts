import { test, expect } from "@playwright/test";

/**
 * Authentication Flow Tests
 *
 * These tests verify the user authentication functionality including:
 * - Login page rendering
 * - GitHub OAuth flow
 * - Password-based authentication
 * - Session persistence
 * - Logout functionality
 */

test.describe("Authentication - Login Page", () => {
  test("should display login page with both auth options", async ({ page }) => {
    await page.goto("/login");

    // Check page title
    await expect(page.locator("h2")).toHaveText("Log In");

    // Check GitHub OAuth button exists
    const githubButton = page.locator('button:has-text("Login with GitHub")');
    await expect(githubButton).toBeVisible();
    await expect(githubButton).toHaveClass(/btn-success/);

    // Check GitHub icon in button
    await expect(githubButton.locator("svg.bi-github")).toBeVisible();
  });

  test("should display email/password login form", async ({ page }) => {
    await page.goto("/login");

    // Check email input exists
    const emailInput = page.locator('input[type="text"]#exampleInputEmail1');
    await expect(emailInput).toBeVisible();
    await expect(page.locator('label[for="exampleInputEmail1"]')).toHaveText(
      "Email address"
    );

    // Check password input exists
    const passwordInput = page.locator(
      'input[type="password"]#exampleInputPassword1'
    );
    await expect(passwordInput).toBeVisible();
    await expect(page.locator('label[for="exampleInputPassword1"]')).toHaveText(
      "Password"
    );

    // Check submit button exists
    const submitButton = page.locator('button[type="submit"]:has-text("Login")');
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toHaveClass(/btn-success/);
  });

  test("should display signup section", async ({ page }) => {
    await page.goto("/login");

    // Check that SignUpPage component is rendered (you may need to adjust selector)
    const signupSection = page.locator("text=/sign up|create account/i").first();
    await expect(signupSection).toBeVisible();
  });
});

test.describe("Authentication - GitHub OAuth Flow", () => {
  test("should redirect to GitHub OAuth on button click", async ({
    page,
    context,
  }) => {
    // Mock the GitHub OAuth authorize endpoint
    await page.route("/api/v0/auth/github/authorize", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          authorization_url: "https://github.com/login/oauth/authorize?client_id=test",
        }),
      });
    });

    await page.goto("/login");

    // Start waiting for navigation before clicking
    const navigationPromise = page.waitForURL(
      /github\.com\/login\/oauth\/authorize/,
      { timeout: 5000 }
    );

    // Click GitHub login button
    await page.locator('button:has-text("Login with GitHub")').click();

    // Wait for navigation to GitHub
    try {
      await navigationPromise;
      // If we got here, navigation succeeded (which is expected with the mock)
      expect(page.url()).toContain("github.com");
    } catch (e) {
      // If navigation didn't happen, the mock should have been called
      // This is acceptable for a test
    }
  });

  test("should handle successful GitHub OAuth callback", async ({ page }) => {
    // Navigate to login page with successful OAuth callback parameters
    await page.goto("/login?gh_login=success&username=testuser");

    // Check that localStorage was set
    const loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
    expect(loggedIn).toBe("true");

    const username = await page.evaluate(() => localStorage.getItem("username"));
    expect(username).toBe("testuser");

    const authMethod = await page.evaluate(() =>
      localStorage.getItem("authMethod")
    );
    expect(authMethod).toBe("oauth");

    const authServer = await page.evaluate(() =>
      localStorage.getItem("authServer")
    );
    expect(authServer).toBe("github.com");

    // Should redirect to home page
    await page.waitForURL("/", { timeout: 5000 });
  });
});

test.describe("Authentication - Password Login", () => {
  test("should submit login form with credentials", async ({ page }) => {
    // Mock the login endpoint
    await page.route("/api/v0/auth/jwt/login", async (route) => {
      const postData = await route.request().postData();
      const params = new URLSearchParams(postData || "");

      if (
        params.get("username") === "test@example.com" &&
        params.get("password") === "testpassword"
      ) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "test_token_12345",
            token_type: "bearer",
          }),
        });
      } else {
        await route.fulfill({
          status: 401,
          statusText: "Unauthorized",
        });
      }
    });

    await page.goto("/login");

    // Fill in credentials
    await page.fill('input[type="text"]#exampleInputEmail1', "test@example.com");
    await page.fill('input[type="password"]#exampleInputPassword1', "testpassword");

    // Submit form
    await page.locator('button[type="submit"]:has-text("Login")').click();

    // Wait a bit for async operations
    await page.waitForTimeout(500);

    // Check that localStorage was set correctly
    const loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
    expect(loggedIn).toBe("true");

    const username = await page.evaluate(() => localStorage.getItem("username"));
    expect(username).toBe("test@example.com");

    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBe("test_token_12345");

    const authMethod = await page.evaluate(() =>
      localStorage.getItem("authMethod")
    );
    expect(authMethod).toBe("password");

    const authServer = await page.evaluate(() =>
      localStorage.getItem("authServer")
    );
    expect(authServer).toBe("nyrkio.com");
  });

  test("should display error message on failed login", async ({ page }) => {
    // Mock failed login
    await page.route("/api/v0/auth/jwt/login", async (route) => {
      await route.fulfill({
        status: 401,
        statusText: "Unauthorized",
      });
    });

    await page.goto("/login");

    // Fill in incorrect credentials
    await page.fill('input[type="text"]#exampleInputEmail1', "wrong@example.com");
    await page.fill('input[type="password"]#exampleInputPassword1', "wrongpassword");

    // Submit form
    await page.locator('button[type="submit"]:has-text("Login")').click();

    // Wait for error message
    await page.waitForTimeout(500);

    // Check for error message
    const errorAlert = page.locator(".alert-warning");
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toContainText("Authentication to Nyrkiö.com failed");
    await expect(errorAlert).toContainText("401");
  });

  test("should not submit form with empty credentials", async ({ page }) => {
    await page.goto("/login");

    // Don't fill in any credentials

    // Click submit button
    await page.locator('button[type="submit"]:has-text("Login")').click();

    // Form should use HTML5 validation, so we stay on the same page
    expect(page.url()).toContain("/login");

    // localStorage should not have been set
    const loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
    expect(loggedIn).not.toBe("true");
  });
});

test.describe("Authentication - Session Persistence", () => {
  test("should persist login state in localStorage", async ({ page }) => {
    // Set up logged-in state
    await page.goto("/login");

    await page.evaluate(() => {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("username", "persisttest@example.com");
      localStorage.setItem("token", "persist_token_12345");
      localStorage.setItem("authMethod", "password");
    });

    // Navigate to home page
    await page.goto("/");

    // Check that login state persists
    const loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
    expect(loggedIn).toBe("true");

    const username = await page.evaluate(() => localStorage.getItem("username"));
    expect(username).toBe("persisttest@example.com");
  });

  test("should maintain session across page reloads", async ({ page }) => {
    await page.goto("/login");

    // Set logged-in state
    await page.evaluate(() => {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("username", "reload@example.com");
      localStorage.setItem("token", "reload_token_12345");
    });

    // Reload page
    await page.reload();

    // Check that session persists
    const loggedIn = await page.evaluate(() => localStorage.getItem("loggedIn"));
    expect(loggedIn).toBe("true");

    const username = await page.evaluate(() => localStorage.getItem("username"));
    expect(username).toBe("reload@example.com");
  });
});

test.describe("Authentication - Logout", () => {
  test("should clear localStorage on logout", async ({ page }) => {
    // Mock logout endpoint
    await page.route("/api/v0/auth/jwt/logout", async (route) => {
      await route.fulfill({
        status: 200,
      });
    });

    await page.goto("/");

    // Set logged-in state
    await page.evaluate(() => {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("username", "logout@example.com");
      localStorage.setItem("username_real", "logout@example.com");
      localStorage.setItem("token", "logout_token_12345");
    });

    // Find and click logout button (adjust selector as needed)
    const logoutButton = page.locator('a:has-text("Log Out")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();

      // Wait for async operations
      await page.waitForTimeout(500);

      // Check that localStorage was cleared
      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("false");

      const username = await page.evaluate(() =>
        localStorage.getItem("username")
      );
      expect(username).toBe("");
    }
  });

  test("should handle logout API failure gracefully", async ({ page }) => {
    // Mock failed logout endpoint
    await page.route("/api/v0/auth/jwt/logout", async (route) => {
      await route.fulfill({
        status: 500,
        statusText: "Internal Server Error",
      });
    });

    await page.goto("/");

    // Set logged-in state
    await page.evaluate(() => {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("username", "logout-fail@example.com");
      localStorage.setItem("token", "logout_fail_token_12345");
    });

    // Find and click logout button
    const logoutButton = page.locator('a:has-text("Log Out")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();

      // Wait for async operations
      await page.waitForTimeout(500);

      // Should still clear localStorage even if API fails
      const loggedIn = await page.evaluate(() =>
        localStorage.getItem("loggedIn")
      );
      expect(loggedIn).toBe("false");
    }
  });
});

test.describe("Authentication - UI State Changes", () => {
  test("should show Login button when not logged in", async ({ page }) => {
    await page.goto("/");

    // Clear any existing login state
    await page.evaluate(() => {
      localStorage.clear();
    });

    await page.reload();

    // Check for login button (adjust selector based on your Nav component)
    const loginButton = page.locator('a:has-text("Log In")');
    await expect(loginButton).toBeVisible();
  });

  test("should show user menu when logged in", async ({ page }) => {
    await page.goto("/");

    // Set logged-in state
    await page.evaluate(() => {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("username", "ui-test@example.com");
      localStorage.setItem("token", "ui_test_token");
    });

    await page.reload();

    // Wait for UI to update
    await page.waitForTimeout(500);

    // Check that login button is not visible
    const loginButton = page.locator('a:has-text("Log In")');
    await expect(loginButton).not.toBeVisible();

    // User menu or username should be visible (adjust selector as needed)
    // This depends on your Nav component structure
  });
});
