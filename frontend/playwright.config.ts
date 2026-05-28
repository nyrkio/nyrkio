import { defineConfig } from "@playwright/test";

const env = (globalThis as any).process?.env || {};
const baseURL = env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173";

export default defineConfig({
  // Run your local dev server before starting the tests
  webServer: env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: "npm run dev",
        url: baseURL,
        reuseExistingServer: !env.CI,
      },

  use: {
    baseURL,
  },
  reporter: [
    ["list"],
    ["json", { outputFile: "test-results/test-results.json" }],
    ["html"],
    [
      "./playwright.nyrkio.reporter.ts",
      {
        gitRepo: "https://github.com/nyrkio/nyrkio",
        projectName: "NyrkioFrontend",
      },
    ],
  ],
});
