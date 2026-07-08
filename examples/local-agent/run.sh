#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="$(mktemp -d)"
OUT_FILE="$OUT_DIR/local_agent_demo.json"

cat > "$OUT_FILE" <<'JSON'
{
  "example": "local-agent",
  "subject": "local-developer-agent",
  "action": "read",
  "resource": "repository-docs",
  "policy_verdict": "ALLOW",
  "network": "not_used",
  "state_change": false
}
JSON

echo "PASS local-agent example: $OUT_FILE"
