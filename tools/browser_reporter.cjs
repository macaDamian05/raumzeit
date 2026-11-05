const fs = require("node:fs");
const path = require("node:path");

class BrowserReporter {
  onBegin(config, suite) {
    this.started = new Date().toISOString(); this.scenarios = [];
    this.expectedTotal = suite.allTests().length;
  }
  onTestEnd(test, result) {
    const project = test.parent.project().name;
    const passed = result.status === "passed";
    this.scenarios.push({
      id: `${project}-${test.title.split(" ")[0]}`,
      name: test.title,
      project,
      browser_version: test.annotations.find((item) => item.type === "browserVersion")?.description,
      expected: "Alle im Test hinterlegten UI-, HTTP- und Zustandsassertionen erfüllt",
      observed: passed ? "Assertions im echten Chromium-Browser bestanden" : (result.error?.message || result.status),
      status: result.status,
      passed,
      duration_ms: result.duration,
    });
  }
  onEnd(result) {
    const root = path.resolve(__dirname, "..");
    const data = {
      started_utc: this.started, timestamp_utc: new Date().toISOString(),
      executor: "KI-gestützt erstellte und ausgeführte Playwright-Tests; keine persönliche Abnahme durch Justin Kolar",
      method: "Wiederholbare Playwright-Testdateien, reale HTTP-Anwendung und isolierte SQLite-Datei; keine API-Mocks",
      framework_version: require("@playwright/test/package.json").version,
      browser: "Chromium", status: result.status,
      expected_total: this.expectedTotal,
      viewports: { desktop: { width: 1280, height: 900 }, mobile: { width: 390, height: 844 } },
      fixed_browser_date: "2026-10-26T08:00:00Z",
      python_coverage_included: false,
      scenarios: this.scenarios,
      limits: "Ein Browser, zwei Viewports. Keine vollständige Browsermatrix, Screenreaderprüfung oder JavaScript-Abdeckungsmessung.",
    };
    fs.mkdirSync(path.join(root, "output", "tests"), { recursive: true });
    fs.writeFileSync(path.join(root, "output", "tests", "browser.json"), JSON.stringify(data, null, 2));
  }
}
module.exports = BrowserReporter;
