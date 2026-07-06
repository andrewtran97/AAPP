#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-.aapp/evidence/agent-black-box-e2e}"
SRC="$OUT/sources"
HOOK="$SRC/hook"
MCP="$SRC/mcp"
GITCI="$SRC/git-ci"
BUNDLE_OUT="$OUT/session-bundle"
BUNDLE="$BUNDLE_OUT/AGENT-BLACK-BOX-BUNDLE"

rm -rf "$OUT"
mkdir -p "$HOOK" "$MCP" "$GITCI"

echo "== E2E 1: hook gateway capture =="
AAPP_BLACKBOX_OUT="$HOOK" python3 -m aapp.agent_blackbox_hook < tests/fixtures/agent_hook_pretool_bash.json >/tmp/aapp_e2e_hook_allow.out
AAPP_BLACKBOX_OUT="$HOOK" python3 -m aapp.agent_blackbox_hook < tests/fixtures/agent_hook_pretool_blocked_bash.json > "$OUT/hook_deny.json"
grep -q '"permissionDecision": "deny"' "$OUT/hook_deny.json"
python3 -m aapp.agent_blackbox_hook verify "$HOOK/session.trace.jsonl" --key-file "$HOOK/dev.key"

echo "== E2E 2: MCP proxy recorder =="
python3 -m aapp.mcp_proxy_recorder record \
  --request tests/fixtures/mcp_tools_call_request.json \
  --response tests/fixtures/mcp_tools_call_response.json \
  --out "$MCP" \
  --session-id "e2e-product-run"

python3 -m aapp.mcp_proxy_recorder record \
  --request tests/fixtures/mcp_blocked_tools_call_request.json \
  --out "$MCP" \
  --session-id "e2e-product-run"

python3 -m aapp.mcp_proxy_recorder verify "$MCP/mcp.trace.jsonl" --key-file "$MCP/dev.key"
python3 -m aapp.mcp_proxy_recorder report "$MCP/mcp.trace.jsonl" --out "$MCP/mcp.report.md"

echo "== E2E 3: Git/CI evidence capture =="
python3 -m aapp.git_ci_evidence capture \
  --repo . \
  --out "$GITCI" \
  --session-id "e2e-product-run"

python3 -m aapp.git_ci_evidence verify "$GITCI/gitci.trace.jsonl" --key-file "$GITCI/dev.key"
python3 -m aapp.git_ci_evidence report "$GITCI/gitci.trace.jsonl" --out "$GITCI/gitci.report.md"

echo "== E2E 4: unified session bundle =="
python3 -m aapp.session_bundle create \
  --hook-trace "$HOOK/session.trace.jsonl" \
  --mcp-trace "$MCP/mcp.trace.jsonl" \
  --git-ci-trace "$GITCI/gitci.trace.jsonl" \
  --out "$BUNDLE_OUT" \
  --session-id "e2e-product-run"

python3 -m aapp.session_bundle verify "$BUNDLE" --key-file "$BUNDLE_OUT/dev.key"
python3 -m aapp.session_bundle report "$BUNDLE" --out "$BUNDLE/session.report.md"

echo "== E2E 5: GitHub Action verifier core command =="
python3 -m aapp.session_bundle verify "$BUNDLE" --key-file "$BUNDLE_OUT/dev.key"
python3 -m aapp.session_bundle report "$BUNDLE" --out "$OUT/github-action-style-report.md"

echo "== E2E 6: tamper rejection =="
cp "$BUNDLE/manifest.json" "$BUNDLE/manifest.backup.json"

AAPP_E2E_OUT="$OUT" python3 - <<'AAPP_E2E_TAMPER_PY'
from pathlib import Path
import json
import os

bundle_root = Path(os.environ["AAPP_E2E_OUT"]) / "session-bundle" / "AGENT-BLACK-BOX-BUNDLE"
manifest = bundle_root / "manifest.json"
obj = json.loads(manifest.read_text(encoding="utf-8"))
obj["session_id"] = "tampered"
manifest.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
AAPP_E2E_TAMPER_PY

if python3 -m aapp.session_bundle verify "$BUNDLE" --key-file "$BUNDLE_OUT/dev.key"; then
  echo "FAIL: tampered E2E bundle verified"
  exit 1
else
  echo "PASS: tampered E2E bundle rejected"
fi

mv "$BUNDLE/manifest.backup.json" "$BUNDLE/manifest.json"

cat > "$OUT/PRODUCT_RUN_SUMMARY.txt" <<EOF
Agent Black Box E2E product run: PASS

Outputs:
- Hook trace: $HOOK/session.trace.jsonl
- MCP trace: $MCP/mcp.trace.jsonl
- Git/CI trace: $GITCI/gitci.trace.jsonl
- Bundle: $BUNDLE
- Session report: $BUNDLE/session.report.md
- GitHub Action style report: $OUT/github-action-style-report.md

Verified:
- hook trace
- MCP trace
- Git/CI trace
- unified bundle
- tamper rejection
EOF

echo
cat "$OUT/PRODUCT_RUN_SUMMARY.txt"
