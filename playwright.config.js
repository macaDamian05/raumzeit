const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./browser_tests",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  expect: { timeout: 7000 },
  outputDir: "output/playwright/artifacts",
  reporter: [
    ["list"],
    ["json", { outputFile: "output/playwright/results.json" }],
    ["junit", { outputFile: "output/playwright/junit.xml" }],
    ["./tools/browser_reporter.cjs"],
  ],
  use: {
    baseURL: "http://127.0.0.1:5051",
    locale: "de-DE",
    timezoneId: "Europe/Berlin",
    browserName: "chromium",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: {
    command: "node tools/browser_server.cjs",
    url: "http://127.0.0.1:5051/api/config",
    reuseExistingServer: false,
    timeout: 30000,
    gracefulShutdown: { signal: "SIGTERM", timeout: 3000 },
  },
});
