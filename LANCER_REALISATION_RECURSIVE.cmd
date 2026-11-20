@echo off
setlocal
REM This launcher executes an explicit, already-locked private composition.
REM It does not select a Kristal, approval, runtime or GF binary implicitly.
set "SPEK_ROOT=%~dp0"
py -3.12 "%SPEK_ROOT%scripts\realiser_composition_semantik.py" --spek-root "%SPEK_ROOT%." %*
exit /b %ERRORLEVEL%
