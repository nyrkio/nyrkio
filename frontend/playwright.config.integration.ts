import { defineConfig } from "@playwright/test";

/**
 * Integration Test Configuration
 *
 * This configuration runs tests against the real backend API.
 * It automatically starts both the frontend dev server and the backend API.
 *
 * Requirements:
 * - MongoDB must be running
 * - .env.backend must be configured
 * - Poetry dependencies must be installed in backend/
 *
 * Usage:
 *   npx playwright test --config=playwright.config.integration.ts
 */
export default defineConfig({
  // Increase timeout for integration tests since they're slower
  timeout: 60000, // 60 seconds per test

  // Run tests serially to avoid conflicts with shared backend state
  workers: 1,

  // Note: Frontend and backend servers must be running before tests
  // Start frontend with: npm run dev
  // Backend should already be running via nyrkio_backend.py

  use: {
    baseURL: "http://localhost:5173",

    // Slower action timeout for integration tests
    actionTimeout: 15000,

    // Record traces on failure for debugging
    trace: "on-first-retry",

    // Take screenshots on failure
    screenshot: "only-on-failure",

    // Record video on failure
    video: "retain-on-failure",
  },

  // Retry failed tests once in case of flakiness
  retries: process.env.CI ? 2 : 1,

  reporter: [
    ["list"],
    ["json", { outputFile: "integration-test-results/results.json" }],
    ["html", { outputFolder: "integration-test-results/html-report" }],
  ],

  // Test directory for integration tests
  testDir: "./tests/integration",

  // Test match pattern
  testMatch: "**/*.integration.ts",
});
