@echo off
REM ============================================================================
REM  AURORA-SATCOM Demo — double-click installer (Windows)
REM  Calls install.ps1 with execution policy bypass for this process only.
REM  No admin / registry changes.
REM ============================================================================

setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\install.ps1"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo Installation completed successfully.
) else (
    echo Installation finished with exit code %RC%.
)
echo.
pause
exit /b %RC%
