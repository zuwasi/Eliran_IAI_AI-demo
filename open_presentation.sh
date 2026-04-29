#!/usr/bin/env bash
# =============================================================================
#  Open the AURORA-SATCOM customer presentations in your default browser.
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

open_url() {
    local target="$1"
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$target" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "$target"
    else
        echo "Please open this file manually in your browser:"
        echo "  $target"
    fi
}

open_url "$ROOT_DIR/how_to_run_the_demo.html"
open_url "$ROOT_DIR/satcom_requirements_presentation.html"
