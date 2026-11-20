@echo off
setlocal
cd /d "%~dp0"
py -3.12 scripts\pilote_agriculture_sol.py --help
if errorlevel 1 pause
endlocal
