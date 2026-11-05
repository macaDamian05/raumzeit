@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Bitte zuerst Einrichtung.cmd ausfuehren.
  pause
  exit /b 1
)
echo Raumzeit mit Beispieldaten: http://127.0.0.1:5050
echo Im Browser oeffnen. Beenden mit Strg+C.
".venv\Scripts\python.exe" -m raumzeit --demo
pause
