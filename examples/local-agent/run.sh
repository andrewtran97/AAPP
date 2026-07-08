#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import datetime
import hashlib
import json
import pathlib
import tempfile

payload = {
"example": "local-agent",
"subject": "local-developer-agent",
"action": "read",
"resource": "repository-docs",
"policy_verdict": "ALLOW",
"identity_binding": "local-demo-identity",
"state_change": False,
"network": "not_used",
"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
payload["digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()

out_dir = pathlib.Path(tempfile.mkdtemp(prefix="aapp-local-agent-"))
out_file = out_dir / "local_agent_demo.json"
out_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(f"PASS local-agent example: {out_file}")
PY
