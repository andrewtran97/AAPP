#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-evidence/a1-mcp-boundary}"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "== A1: record local MCP-style tool decisions =="
python3 -m aapp.cli mcp-record \
  --policy examples/mcp-recorder-adapter/policy.demo.json \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --out "$OUT_DIR/recorded"

echo "== A1: replay local MCP-style trace =="
python3 -m aapp.cli replay \
  --trace "$OUT_DIR/recorded/trace.jsonl" \
  --key-file "$OUT_DIR/recorded/dev.key" \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --out "$OUT_DIR/replay_report.md"

echo "== A1: bundle local MCP boundary evidence =="
python3 -m aapp.cli bundle \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --trace "$OUT_DIR/recorded/trace.jsonl" \
  --key-file "$OUT_DIR/recorded/dev.key" \
  --report "$OUT_DIR/replay_report.md" \
  --out "$OUT_DIR/AAPP-EVIDENCE-BUNDLE"

echo "== A1: verify proof points =="
grep -q "blocked_api_call" "$OUT_DIR/replay_report.md"
grep -q "require_human_approval" "$OUT_DIR/replay_report.md"
grep -q "deny" "$OUT_DIR/replay_report.md"
grep -q "allow" "$OUT_DIR/replay_report.md"
grep -q "Record hash" "$OUT_DIR/replay_report.md"
grep -q "Parent hash" "$OUT_DIR/replay_report.md"

while IFS= read -r f; do
  test -f "$OUT_DIR/$f" || { echo "FAIL: missing $OUT_DIR/$f"; exit 1; }
  echo "OK: $OUT_DIR/$f"
done <<'EOF'
recorded/trace.jsonl
recorded/dev.key
recorded/mcp-results.json
recorded/verification_result.md
replay_report.md
AAPP-EVIDENCE-BUNDLE/scope.json
AAPP-EVIDENCE-BUNDLE/trace.jsonl
AAPP-EVIDENCE-BUNDLE/evidence.bundle.json
AAPP-EVIDENCE-BUNDLE/evidence.report.md
AAPP-EVIDENCE-BUNDLE/hashes.txt
AAPP-EVIDENCE-BUNDLE/verification_result.md
EOF

echo "PASS: A1 MCP boundary local research output built at $OUT_DIR"
