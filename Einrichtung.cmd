@echo off
setlocal
cd /d "%~dp0"
echo Python 3.12 oder neuer wird benoetigt.
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>nul
if errorlevel 1 (
  python -m venv .venv
) else (
  py -3 -m venv .venv
)
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto failed
echo Einrichtung abgeschlossen. Demo_starten.cmd oder Starten.cmd oeffnen.
pause
exit /b 0
:failed
echo Einrichtung fehlgeschlagen. Bitte die Fehlermeldung oben pruefen.
pause
exit /b 1
