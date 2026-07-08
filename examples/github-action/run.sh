#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="$(mktemp -d)"
OUT_FILE="$OUT_DIR/github_action_demo.json"

cat > "$OUT_FILE" <<'JSON'
{
  "example": "github-action",
  "event": "pull_request",
  "repository": "local/aapp-demo",
  "actor": "local-developer",
  "policy_precheck": "read_only_example",
  "secrets_required": false,
  "network": "not_used",
  "artifact_upload": false
}
JSON

echo "PASS github-action example: $OUT_FILE"
