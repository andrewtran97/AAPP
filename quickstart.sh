#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
export PYTHONDONTWRITEBYTECODE=1

echo "== AAPP B27C Developer Quickstart =="

test -f docs/phase-notes/B27C_SCOPE.md
test -f docs/CLAIM_BOUNDARIES.md
test -f examples/local-agent/README.md
test -x examples/local-agent/run.sh
test -f examples/github-action/README.md
test -x examples/github-action/run.sh
test -f examples/mcp-tool-call/README.md
test -x examples/mcp-tool-call/run.sh
test -f README.md

bash examples/local-agent/run.sh
bash examples/github-action/run.sh
bash examples/mcp-tool-call/run.sh

if [ -f scripts/check_phase_manifest.py ]; then
  python3 scripts/check_phase_manifest.py
fi

if [ -f scripts/check_claim_boundaries.py ]; then
  python3 scripts/check_claim_boundaries.py
fi

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

echo "PASS: B27C quickstart completed"
