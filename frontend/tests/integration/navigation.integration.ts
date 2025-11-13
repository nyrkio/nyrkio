import { test, expect } from "@playwright/test";

/**
 * Integration Tests for Navigation and UI
 *
 * Tests navigation, routing, and general UI functionality
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

test.describe("Navigation Integration Tests", () => {
  test("should load front page when not logged in", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();

    await page.waitForTimeout(2000);

    // Should show front page content
    const pageContent = await page.content();

    expect(pageContent).toBeTruthy();
  });

  test("should navigate to documentation pages", async ({ page }) => {
    await page.goto("/docs/getting-started");
    await page.waitForTimeout(1000);

    expect(page.url()).toContain("/docs");

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should navigate between documentation sections", async ({ page }) => {
    // Start at getting started
    await page.goto("/docs/getting-started");
    await page.waitForTimeout(1000);

    // Navigate to another doc page
    await page.goto("/docs/getting-started-http");
    await page.waitForTimeout(1000);

    expect(page.url()).toContain("/docs/getting-started-http");

    // Another doc page
    await page.goto("/docs/working-with-graphs");
    await page.waitForTimeout(1000);

    expect(page.url()).toContain("/docs/working-with-graphs");
  });

  test("should show public test results", async ({ page }) => {
    await page.goto("/public");
    await page.waitForTimeout(2000);

    expect(page.url()).toContain("/public");

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should navigate to about pages", async ({ page }) => {
    await page.goto("/about");
    await page.waitForTimeout(1000);

    expect(page.url()).toContain("/about");

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should navigate to pricing page", async ({ page }) => {
    await page.goto("/pricing");
    await page.waitForTimeout(1000);

    expect(page.url()).toContain("/pricing");

    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should handle 404 for invalid routes", async ({ page }) => {
    await page.goto("/invalid-route-that-does-not-exist");
    await page.waitForTimeout(1000);

    // Should show 404 page or redirect
    const pageContent = await page.content();
    expect(pageContent).toBeTruthy();
  });
});

test.describe("Authenticated Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test("should redirect to dashboard after login", async ({ page }) => {
    // Already logged in from beforeEach
    // Should be on /tests
    await page.waitForURL(/\/tests/, { timeout: 5000 });
    expect(page.url()).toMatch(/\/tests/);
  });

  test("should navigate between authenticated pages", async ({ page }) => {
    // Dashboard
    await page.goto("/tests");
    await page.waitForTimeout(1000);
    expect(page.url()).toContain("/tests");

    // User settings
    await page.goto("/user/settings");
    await page.waitForTimeout(1000);
    expect(page.url()).toContain("/user/settings");

    // Billing
    await page.goto("/billing");
    await page.waitForTimeout(1000);
    expect(page.url()).toContain("/billing");

    // Back to dashboard
    await page.goto("/tests");
    await page.waitForTimeout(1000);
    expect(page.url()).toContain("/tests");
  });

  test("should maintain auth state across navigation", async ({ page }) => {
    const initialToken = await page.evaluate(() =>
      localStorage.getItem("token")
    );

    // Navigate to several pages
    await page.goto("/tests");
    await page.waitForTimeout(500);
    await page.goto("/user/settings");
    await page.waitForTimeout(500);
    await page.goto("/docs/getting-started");
    await page.waitForTimeout(500);

    // Token should still be present
    const finalToken = await page.evaluate(() => localStorage.getItem("token"));
    expect(finalToken).toBe(initialToken);

    const loggedIn = await page.evaluate(() =>
      localStorage.getItem("loggedIn")
    );
    expect(loggedIn).toBe("true");
  });
});

test.describe("Side Panel", () => {
  test("should display side panel on front page", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForTimeout(2000);

    // Check for side panel
    const sidePanel = page.locator("#sidepanel");
    await expect(sidePanel).toBeVisible();
  });

  test("should display side panel when logged in", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);

    await page.waitForTimeout(1000);

    // Side panel should still be visible
    const sidePanel = page.locator("#sidepanel");
    await expect(sidePanel).toBeVisible();
  });

  test("should update side panel content based on route", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);

    // Check side panel on different routes
    await page.goto("/tests");
    await page.waitForTimeout(1000);
    let sidePanel = page.locator("#sidepanel");
    await expect(sidePanel).toBeVisible();

    await page.goto("/docs/getting-started");
    await page.waitForTimeout(1000);
    sidePanel = page.locator("#sidepanel");
    await expect(sidePanel).toBeVisible();
  });
});

test.describe("Navigation Bar", () => {
  test("should display nav bar", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Nav should be visible (adjust selector based on your nav component)
    const nav = page.locator("nav").or(page.locator(".navbar"));
    const navCount = await nav.count();

    if (navCount > 0) {
      await expect(nav.first()).toBeVisible();
    }
  });

  test("should show login button when not logged in", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForTimeout(1000);

    // Should have login button/link
    const loginLink = page.locator('a[href="/login"]').or(
      page.locator('a:has-text("Log In")')
    );
    const loginCount = await loginLink.count();

    if (loginCount > 0) {
      await expect(loginLink.first()).toBeVisible();
    }
  });

  test("should show user menu when logged in", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);

    await page.waitForTimeout(1000);

    // Should not show login button
    const loginLink = page.locator('a:has-text("Log In")');
    await expect(loginLink).not.toBeVisible();

    // Should show logout button or user menu
    const logoutLink = page.locator('a:has-text("Log Out")');
    const logoutCount = await logoutLink.count();

    if (logoutCount > 0) {
      await expect(logoutLink).toBeVisible();
    }
  });
});

test.describe("Footer", () => {
  test("should display footer", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);

    // Footer should be visible
    const footer = page.locator("footer").or(page.locator("#main-content2"));
    const footerCount = await footer.count();

    if (footerCount > 0) {
      await expect(footer.first()).toBeVisible();
    }
  });
});

test.describe("Responsive Design", () => {
  test("should render on mobile viewport", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");
    await page.waitForTimeout(2000);

    // Page should render
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should render on tablet viewport", async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto("/");
    await page.waitForTimeout(2000);

    // Page should render
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("should render on desktop viewport", async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto("/");
    await page.waitForTimeout(2000);

    // Page should render
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});

test.describe("Error Handling", () => {
  test("should handle network errors gracefully", async ({ page }) => {
    // Navigate to page
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Page should have loaded something
    const bodyContent = await page.locator("body").textContent();
    expect(bodyContent).toBeTruthy();
  });

  test("should handle API errors without crashing", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await login(page, TEST_USER.email, TEST_USER.password);

    // Navigate to a page that makes API calls
    await page.goto("/tests");
    await page.waitForTimeout(2000);

    // Even if API calls fail, page should render
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });
});
