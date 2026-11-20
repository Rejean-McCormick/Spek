@echo off
setlocal
set "SPEK=C:\mycode\Spek_Semantic-publishing\Spek"
py -3.12 "%SPEK%\scripts\piloter_agriculture_registres.py" --spek-root "%SPEK%" probe-dik
pause
