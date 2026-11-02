@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0VERIFIER_INSTALLATION_SPEK.py"
) else (
  python "%~dp0VERIFIER_INSTALLATION_SPEK.py"
)
if errorlevel 1 (
  echo.
  echo Verification echouee : le depot contient des fichiers manquants.
)
pause
