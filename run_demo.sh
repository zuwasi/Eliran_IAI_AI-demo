#!/usr/bin/env bash
# =============================================================================
#  AURORA-SATCOM Demo — re-run the pipeline (Linux / macOS)
#  Requires that ./install.sh has been run successfully at least once.
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
HARNESS="$ROOT_DIR/satcom_requirements_agent_harness"
VENV_PY="$HARNESS/.venv/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
    echo
    echo "  [!!] No virtual environment found."
    echo "       Please run ./install.sh first."
    echo
    exit 1
fi

echo
echo "  Running SATCOM Requirements Agent pipeline..."
echo

cd "$HARNESS"
"$VENV_PY" src/main.py --config config.json
RC=$?

echo
if [[ "$RC" == "0" ]]; then
    echo "  [OK] Pipeline finished. Outputs are in: outputs/"
else
    echo "  [!!] Pipeline failed with exit code $RC."
    echo "       See outputs/validation_report.json for details."
fi
echo
exit "$RC"
