#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-evidence/public-demo}"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "== Build local MCP-style recorded trace =="
python3 -m aapp.cli mcp-record \
  --policy examples/mcp-recorder-adapter/policy.demo.json \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --out "$OUT_DIR/recorded"

echo "== Build replay report =="
python3 -m aapp.cli replay \
  --trace "$OUT_DIR/recorded/trace.jsonl" \
  --key-file "$OUT_DIR/recorded/dev.key" \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --out "$OUT_DIR/replay_report.md"

echo "== Build evidence bundle =="
python3 -m aapp.cli bundle \
  --scope examples/mcp-recorder-adapter/scope.demo.json \
  --trace "$OUT_DIR/recorded/trace.jsonl" \
  --key-file "$OUT_DIR/recorded/dev.key" \
  --report "$OUT_DIR/replay_report.md" \
  --out "$OUT_DIR/AAPP-EVIDENCE-BUNDLE"

cat > "$OUT_DIR/README.md" <<'MD'
# AAPP Public Demo

This demo is local only.

It does not contact:
- a live MCP server
- a network target
- an external service
- a real vendor system
- a credential store

## Expected output

```text
evidence/public-demo/
  README.md
  recorded/
    trace.jsonl
    dev.key
    mcp-results.json
    verification_result.md
  replay_report.md
  AAPP-EVIDENCE-BUNDLE/
    scope.json
    trace.jsonl
    evidence.bundle.json
    evidence.report.md
    hashes.txt
    verification_result.md
```

## What this proves

- local MCP-style tool decisions can be recorded
- denied tool calls are preserved as denied records
- approval-required calls are visible in replay
- the trace verifies through AAPP
- the evidence bundle contains manifest, hashes, report, scope, trace, and verification result

## What this does not claim

- no live MCP integration
- no production security certification
- no post-quantum security
- no Qubes certification
- no government affiliation
- no compliance guarantee
- no exploit capability
MD

echo "PASS: public demo built at $OUT_DIR"
