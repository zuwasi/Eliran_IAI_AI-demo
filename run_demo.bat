@echo off
REM ============================================================================
REM  AURORA-SATCOM Demo — re-run the pipeline (Windows)
REM  Requires that install.bat has been run successfully at least once.
REM ============================================================================

setlocal
cd /d "%~dp0\satcom_requirements_agent_harness"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo  [!!] No virtual environment found.
    echo       Please run install.bat first.
    echo.
    pause
    exit /b 1
)

echo.
echo  Running SATCOM Requirements Agent pipeline...
echo.

".venv\Scripts\python.exe" "src\main.py" --config "config.json"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo  [OK] Pipeline finished. Outputs are in: outputs\
) else (
    echo  [!!] Pipeline failed with exit code %RC%.
    echo       See outputs\validation_report.json for details.
)
echo.
pause
exit /b %RC%
