#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONDONTWRITEBYTECODE=1

echo "== AAPP B27C Developer Quickstart =="

REQUIRED_FILES=(
"docs/phase-notes/B27C_SCOPE.md"
"docs/CLAIM_BOUNDARIES.md"
"quickstart.sh"
"examples/local-agent/README.md"
"examples/local-agent/run.sh"
"examples/github-action/README.md"
"examples/github-action/run.sh"
"examples/mcp-tool-call/README.md"
"examples/mcp-tool-call/run.sh"
"README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
if [ ! -f "$file" ]; then
echo "FAIL: missing $file"
exit 1
fi
done

echo "PASS: required files exist"

EXECUTABLE_FILES=(
"quickstart.sh"
"examples/local-agent/run.sh"
"examples/github-action/run.sh"
"examples/mcp-tool-call/run.sh"
)

for file in "${EXECUTABLE_FILES[@]}"; do
if [ ! -x "$file" ]; then
echo "FAIL: not executable $file"
exit 1
fi
done

echo "PASS: scripts executable"

bash examples/local-agent/run.sh
bash examples/github-action/run.sh
bash examples/mcp-tool-call/run.sh

if [ -f scripts/check_claim_boundaries.py ]; then
python3 scripts/check_claim_boundaries.py
fi

if [ -f scripts/check_phase_manifest.py ]; then
python3 scripts/check_phase_manifest.py
fi

find . -type d -name "pycache" -prune -exec rm -rf {} +
find . -type f −name"∗.pyc"−o−name"∗.pyo" -delete

echo "PASS: B27C quickstart completed"
