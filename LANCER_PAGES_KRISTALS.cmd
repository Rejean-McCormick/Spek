@echo off
setlocal
cd /d "%~dp0"
if not exist "scripts\construire_pages_kristals.py" (
  echo ERREUR : scripts\construire_pages_kristals.py manquant.
  exit /b 2
)
py -3.12 "scripts\construire_pages_kristals.py" %*
exit /b %ERRORLEVEL%
