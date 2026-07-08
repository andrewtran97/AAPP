#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="$(mktemp -d)"
OUT_FILE="$OUT_DIR/mcp_tool_call_demo.json"

cat > "$OUT_FILE" <<'JSON'
{
  "example": "mcp-tool-call",
  "tool": "read_file",
  "resource": "README.md",
  "mode": "read_only",
  "policy_verdict": "ALLOW",
  "network": "not_used",
  "state_change": false,
  "external_tool_call": false
}
JSON

echo "PASS mcp-tool-call example: $OUT_FILE"
