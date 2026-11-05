"""Führt Tests aus und bewahrt messbare Ergebnisse für das Portfolio auf."""

from datetime import datetime, timezone
from pathlib import Path
import importlib.metadata
import hashlib
import json
import platform
import sqlite3
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def source_files():
    paths=[]
    for folder in [ROOT/"raumzeit",ROOT/"tests",ROOT/"browser_tests"]:
        paths.extend(path for path in folder.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    paths.extend(ROOT/name for name in [
        "requirements.txt","requirements-dev.txt","requirements-portfolio.txt","pyproject.toml",
        "Starten.cmd","Demo_starten.cmd","Pruefung_starten.cmd","Einrichtung.cmd","package.json","package-lock.json",
        "playwright.config.js",".prettierrc.json","tools/browser_server.cjs","tools/browser_reporter.cjs",
        "tools/verify_browser.py","tools/browser_app.py",
    ])
    paths.extend(path for path in (ROOT/"tools").glob("*") if path.suffix in {".py", ".cjs", ".js", ".mjs"})
    return [dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in sorted(set(paths))]


def main():
    output = ROOT / "output" / "tests"
    output.mkdir(parents=True, exist_ok=True)
    # Ein neuer Pfad vermeidet das automatische Löschen fremder Temp-Verzeichnisse.
    temporary = ROOT / "output" / "qa" / f"pytest-{uuid.uuid4().hex[:10]}"
    assert temporary.resolve().is_relative_to(ROOT.resolve()) and not temporary.exists()
    temporary.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before=source_files()
    command = [sys.executable,"-m","coverage","run","-m","pytest","-q","--tb=short",f"--basetemp={temporary}",f"--junitxml={output / 'junit.xml'}"]
    result = subprocess.run(command,cwd=ROOT,text=True,encoding="utf-8",errors="replace",capture_output=True)
    (output/"pytest.txt").write_text(result.stdout+result.stderr,encoding="utf-8")
    print(result.stdout, end="")
    print(result.stderr, end="",file=sys.stderr)
    if result.returncode:
        return result.returncode
    if source_files() != before:
        raise RuntimeError("Quellstand während der Tests geändert; Nachweise erneut erzeugen.")
    (output/"source_manifest.json").write_text(json.dumps(dict(verified_utc=datetime.now(timezone.utc).isoformat(),algorithm="SHA-256",files=before),indent=2),encoding="utf-8")
    subprocess.run([sys.executable,"-m","coverage","json","-o",str(output/"coverage.json")],cwd=ROOT,check=True)
    report = subprocess.run([sys.executable,"-m","coverage","report"],cwd=ROOT,text=True,capture_output=True,check=True)
    (output/"coverage.txt").write_text(report.stdout,encoding="utf-8")
    versions = {name:importlib.metadata.version(name) for name in ["Flask","Werkzeug","pytest","coverage"]}
    (output/"environment.json").write_text(json.dumps(dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),platform=platform.system(),sqlite=sqlite3.sqlite_version,packages=versions,exit_code=result.returncode),indent=2),encoding="utf-8")
    print(report.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
