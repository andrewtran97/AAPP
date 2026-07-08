#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import datetime
import hashlib
import json
import pathlib
import tempfile

params = {
"path": "README.md",
"mode": "read_only",
}

params_digest = "sha256:" + hashlib.sha256(
json.dumps(params, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()

payload = {
"example": "mcp-tool-call",
"tool": "read_file",
"params_digest": params_digest,
"policy_verdict": "ALLOW",
"workload_identity": "local-demo-workload",
"state_change": False,
"network": "not_used",
"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
payload["digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()

out_dir = pathlib.Path(tempfile.mkdtemp(prefix="aapp-mcp-tool-call-"))
out_file = out_dir / "mcp_tool_call_demo.json"
out_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(f"PASS mcp-tool-call example: {out_file}")
PY
