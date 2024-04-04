import { defineConfig } from 'playwright/test';

export default defineConfig({
  // Run your local dev server before starting the tests
  webServer: {
    command: 'npm run dev',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: !process.env.CI,
  },

  use: {
    baseURL: 'http://127.0.0.1:5173',
  },
reporter: [
    ['list'],
    ['json', {  outputFile: 'test-results/test-results.json' }],
    ['html'],
    ['./playwright.nyrkio.reporter.ts', {gitRepo: "https://github.com/nyrkio/nyrkio", projectName: "Nyrkiö frontend"}]
  ],

});
