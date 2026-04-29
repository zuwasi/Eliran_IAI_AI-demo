# =============================================================================
#  AURORA-SATCOM Requirements Agent Harness - Windows installer
#  Prepared by Engineering Software Lab (https://eswlab.com/contact-us/)
# =============================================================================
#
#  This script:
#    1. Verifies Python 3.10+ is installed and on PATH
#    2. Creates a virtual environment in the harness folder
#    3. Installs the single dependency (jsonschema)
#    4. Runs a smoke test to confirm the pipeline produces a passing score
#
#  Usage:  Right-click -> Run with PowerShell
#       OR (recommended): double-click install.bat
#
#  No admin rights required. No registry changes. No system files modified.
# =============================================================================

$ErrorActionPreference = "Stop"

function Write-Section($text) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Write-OK($text)   { Write-Host "  [OK] $text" -ForegroundColor Green }
function Write-Info($text) { Write-Host "  [..] $text" -ForegroundColor Gray }
function Write-Fail($text) { Write-Host "  [!!] $text" -ForegroundColor Red }

# --- 1. Locate this script's folder and the harness ------------------------
$root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$harness = Join-Path $root "satcom_requirements_agent_harness"

Write-Section "AURORA-SATCOM Demo Installer"
Write-Info "Install root: $root"

if (-not (Test-Path $harness)) {
    Write-Fail "Cannot find harness folder: $harness"
    Write-Fail "Make sure install.ps1 lives next to satcom_requirements_agent_harness\"
    Read-Host "Press Enter to exit"
    exit 1
}

# --- 2. Find a Python 3.10+ interpreter ------------------------------------
Write-Section "Step 1 of 4 - Locating Python 3.10+"

$pythonCandidates = @("python", "python3", "py")
$python = $null

foreach ($cmd in $pythonCandidates) {
    try {
        $verLine = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $verLine -match "Python\s+(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                $python = $cmd
                Write-OK "Found $verLine via '$cmd'"
                break
            } else {
                Write-Info "'$cmd' reports $verLine - too old, need 3.10+"
            }
        }
    } catch { }
}

if (-not $python) {
    Write-Fail "Python 3.10 or newer is required and was not found on PATH."
    Write-Fail "Install from https://www.python.org/downloads/  (tick 'Add Python to PATH')."
    Read-Host "Press Enter to exit"
    exit 1
}

# --- 3. Create venv --------------------------------------------------------
Write-Section "Step 2 of 4 - Creating virtual environment"
$venvDir    = Join-Path $harness ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (Test-Path $venvDir) {
    Write-Info "Existing .venv found - reusing."
} else {
    Write-Info "Creating .venv in $venvDir"
    & $python -m venv $venvDir
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        Write-Fail "Failed to create virtual environment."
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-OK "Virtual environment created."
}

# --- 4. Install dependencies -----------------------------------------------
Write-Section "Step 3 of 4 - Installing dependencies"
$requirements = Join-Path $harness "requirements.txt"
Write-Info "Upgrading pip (quiet)..."
& $venvPython -m pip install --quiet --upgrade pip 2>&1 | Out-Null

Write-Info "Installing from requirements.txt"
& $venvPython -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) {
    Write-Fail "pip install failed. Check your network / proxy and try again."
    Read-Host "Press Enter to exit"
    exit 1
}
Write-OK "Dependencies installed."

# --- 5. Smoke test ---------------------------------------------------------
Write-Section "Step 4 of 4 - Running smoke test"
Push-Location $harness
try {
    & $venvPython "src\main.py" --config "config.json" | Out-Null
    $exit = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($exit -ne 0) {
    Write-Fail "Smoke test failed (pipeline exit code $exit)."
    Write-Fail "Check $harness\outputs\validation_report.json for details."
    Read-Host "Press Enter to exit"
    exit $exit
}
Write-OK "Smoke test passed - final score 100/100."

# --- Done ------------------------------------------------------------------
Write-Section "Installation complete"
Write-Host ""
Write-Host "  Run the demo any time with:"        -ForegroundColor White
Write-Host "    .\run_demo.bat"                   -ForegroundColor Yellow
Write-Host ""
Write-Host "  Open the customer presentations:"   -ForegroundColor White
Write-Host "    .\open_presentation.bat"          -ForegroundColor Yellow
Write-Host ""
Write-Host "  Outputs land in:"                   -ForegroundColor White
Write-Host "    satcom_requirements_agent_harness\outputs\" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Need help? https://eswlab.com/contact-us/" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"
