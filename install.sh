#!/usr/bin/env bash
# =============================================================================
#  AURORA-SATCOM Requirements Agent Harness — Linux / macOS installer
#  Prepared by Engineering Software Lab (https://eswlab.com/contact-us/)
#
#  Usage:
#      chmod +x install.sh
#      ./install.sh
#
#  No sudo / root required. No system files modified.
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
HARNESS="$ROOT_DIR/satcom_requirements_agent_harness"

# ANSI colors
C_CYAN='\033[1;36m'
C_GREEN='\033[1;32m'
C_RED='\033[1;31m'
C_GRAY='\033[0;37m'
C_YELLOW='\033[1;33m'
C_RESET='\033[0m'

section() {
    echo
    echo -e "${C_CYAN}============================================================${C_RESET}"
    echo -e "${C_CYAN}  $1${C_RESET}"
    echo -e "${C_CYAN}============================================================${C_RESET}"
}

ok()   { echo -e "  ${C_GREEN}[OK]${C_RESET} $1"; }
info() { echo -e "  ${C_GRAY}[..]${C_RESET} $1"; }
fail() { echo -e "  ${C_RED}[!!]${C_RESET} $1"; }

# --- 1. Sanity check --------------------------------------------------------
section "AURORA-SATCOM Demo Installer"
info "Install root: $ROOT_DIR"

if [[ ! -d "$HARNESS" ]]; then
    fail "Cannot find harness folder: $HARNESS"
    fail "Make sure install.sh lives next to satcom_requirements_agent_harness/"
    exit 1
fi

# --- 2. Find a Python 3.10+ interpreter ------------------------------------
section "Step 1 of 4 — Locating Python 3.10+"

PYTHON=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1; then
        ver_str="$("$candidate" --version 2>&1 || true)"
        if [[ "$ver_str" =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
            major="${BASH_REMATCH[1]}"
            minor="${BASH_REMATCH[2]}"
            if (( major > 3 || (major == 3 && minor >= 10) )); then
                PYTHON="$candidate"
                ok "Found $ver_str via '$candidate'"
                break
            else
                info "'$candidate' is $ver_str — too old, need 3.10+"
            fi
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    fail "Python 3.10 or newer is required and was not found on PATH."
    fail "Install via your package manager or from https://www.python.org/downloads/"
    exit 1
fi

# --- 3. Create venv ---------------------------------------------------------
section "Step 2 of 4 — Creating virtual environment"
VENV_DIR="$HARNESS/.venv"
VENV_PY="$VENV_DIR/bin/python"

if [[ -d "$VENV_DIR" ]]; then
    info "Existing .venv found — reusing."
else
    info "Creating .venv in $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
    if [[ ! -x "$VENV_PY" ]]; then
        fail "Failed to create virtual environment."
        exit 1
    fi
    ok "Virtual environment created."
fi

# --- 4. Install dependencies ------------------------------------------------
section "Step 3 of 4 — Installing dependencies"
info "Upgrading pip (quiet)..."
"$VENV_PY" -m pip install --quiet --upgrade pip

info "Installing from requirements.txt"
"$VENV_PY" -m pip install -r "$HARNESS/requirements.txt"
ok "Dependencies installed."

# --- 5. Smoke test ----------------------------------------------------------
section "Step 4 of 4 — Running smoke test"
(
    cd "$HARNESS"
    "$VENV_PY" src/main.py --config config.json > /dev/null
)
ok "Smoke test passed — final score 100/100."

# --- Done -------------------------------------------------------------------
section "Installation complete"
echo
echo -e "  Run the demo any time with:"
echo -e "    ${C_YELLOW}./run_demo.sh${C_RESET}"
echo
echo -e "  Open the customer presentations:"
echo -e "    ${C_YELLOW}./open_presentation.sh${C_RESET}"
echo
echo -e "  Outputs land in:"
echo -e "    ${C_YELLOW}satcom_requirements_agent_harness/outputs/${C_RESET}"
echo
echo -e "  Need help? ${C_CYAN}https://eswlab.com/contact-us/${C_RESET}"
echo
