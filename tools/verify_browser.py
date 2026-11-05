"""Wiederholbare Browserprüfung, getrennt von der Python-Abdeckungsmessung."""

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import shutil
import subprocess
import sys

from verify import ROOT, source_files


def main():
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js fehlt. Bitte die Einrichtung in README.md ausführen.")
    cli = ROOT / "node_modules/@playwright/test/cli.js"
    if not cli.is_file():
        raise RuntimeError("Playwright fehlt. Bitte npm ci und npx playwright install chromium ausführen.")
    before = source_files()
    target = ROOT / "output/tests/browser.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"status": "running", "scenarios": []}), encoding="utf-8")
    environment = dict(os.environ, RAUMZEIT_PYTHON=sys.executable)
    result = subprocess.run([node, str(cli), "test", "--max-failures=1"], cwd=ROOT, env=environment)
    if result.returncode:
        return result.returncode
    if before != source_files():
        raise RuntimeError("Quellstand während der Browserprüfung geändert. Bitte erneut prüfen.")
    report = json.loads(target.read_text(encoding="utf-8"))
    if report.get("status") != "passed" or not report.get("scenarios"):
        raise RuntimeError("Kein vollständiger erfolgreicher Browserbericht vorhanden.")
    expected = {f"{project}-E{index:02d}" for project in ["desktop", "mobile"] for index in range(1, 7)}
    if {case["id"] for case in report["scenarios"]} != expected:
        raise RuntimeError("Browserbericht enthält nicht alle sechs Fälle in beiden Viewports.")
    (ROOT / "output/tests/browser_source_manifest.json").write_text(
        json.dumps({"verified_utc": datetime.now(timezone.utc).isoformat(), "files": before}, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
