@echo off
REM ============================================================================
REM  Open the AURORA-SATCOM customer presentations in your default browser.
REM ============================================================================

setlocal
cd /d "%~dp0"

start "" "how_to_run_the_demo.html"
start "" "satcom_requirements_presentation.html"

exit /b 0
