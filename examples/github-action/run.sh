#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import datetime
import hashlib
import json
import pathlib
import tempfile

payload = {
"example": "github-action",
"event": "pull_request",
"repository": "local/aapp-demo",
"ref": "refs/heads/b27c-developer-distribution-gate",
"actor": "local-developer",
"workflow": "aapp-local-validation",
"policy_precheck": "read_only_example",
"secrets_required": False,
"network": "not_used",
"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
payload["digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()

out_dir = pathlib.Path(tempfile.mkdtemp(prefix="aapp-github-action-"))
out_file = out_dir / "github_action_demo.json"
out_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(f"PASS github-action example: {out_file}")
PY
