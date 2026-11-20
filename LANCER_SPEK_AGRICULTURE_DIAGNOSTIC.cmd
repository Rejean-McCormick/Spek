@echo off
setlocal
set "SPEK_ROOT=%~dp0"
set "STAMP=%RANDOM%-%RANDOM%"
py -3.12 "%SPEK_ROOT%scripts\piloter_agriculture_registres.py" --spek-root "%SPEK_ROOT%." doctor --report "%USERPROFILE%\Downloads\diagnostic-spek-agriculture-%STAMP%.json"
echo.
if errorlevel 1 (
  echo Diagnostic refuse. Inspectez la sortie ci-dessus.
) else (
  echo Rapport prive dans Downloads.
)
pause
