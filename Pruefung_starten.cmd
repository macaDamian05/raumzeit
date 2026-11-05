@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Bitte zuerst Einrichtung.cmd ausfuehren.
  pause
  exit /b 1
)
echo Eigene Pruefung: http://127.0.0.1:5052
echo Getrennte Datenbank: instance\pruefung.sqlite3
echo Ablauf: docs\eigene_pruefung.md. Beenden mit Strg+C.
".venv\Scripts\python.exe" -m raumzeit --port 5052 --database instance\pruefung.sqlite3
pause
