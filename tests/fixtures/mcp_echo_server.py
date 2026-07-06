from __future__ import annotations

import json
import sys

for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue

    request = json.loads(raw)
    response = {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "content": [{"type": "text", "text": "ok"}],
            "isError": False,
        },
    }
    print(json.dumps(response, sort_keys=True, separators=(",", ":")), flush=True)
