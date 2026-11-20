@echo off
setlocal
set "SPEK_ROOT=%~dp0."
py -3.12 "%SPEK_ROOT%scripts\orchestrer_registre_spek.py" --spek-root "%SPEK_ROOT%" inspect --kristal agriculture
if errorlevel 1 (
 echo Refus du controle des registres. Voir docs\POINT_ENTREE_REGISTRES_SPEK.md
 exit /b 2
)
endlocal
