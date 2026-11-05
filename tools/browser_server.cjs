// Eigener Serverprozess für Tests, ohne Zugriff auf instance/ oder echte Nutzerdaten.
const { spawn } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");
const crypto = require("node:crypto");
const root = path.resolve(__dirname, "..");
const python = process.env.RAUMZEIT_PYTHON || path.join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const folder = path.join(root, "output", "qa", `browser-${crypto.randomUUID()}`);
fs.mkdirSync(folder, { recursive: true });
const child = spawn(python, ["tools/browser_app.py", path.join(folder, "browser.sqlite3")], {
  cwd: root, stdio: "inherit", windowsHide: true,
});
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill());
child.on("error", (error) => { console.error(error.message); process.exitCode = 1; });
child.on("exit", (code) => { process.exitCode = code || 0; });
