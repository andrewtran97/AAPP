from __future__ import annotations

import argparse
import http.client
import json
import socket
import time
from pathlib import Path
from typing import Any

from aapp.network_scope import authorize_request, load_scope

SCHEMA_VERSION = "aapp.network_active_scan.v1"

ALLOWED = "ALLOWED"
BLOCKED = "BLOCKED"


def _write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def tcp_connect(target: str, port: int, timeout_s: float) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        with socket.create_connection((target, port), timeout=timeout_s):
            return {
                "status": "open",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "error": None,
            }
    except Exception as exc:
        return {
            "status": "closed_or_unreachable",
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "error": type(exc).__name__,
        }


def http_health(method: str, target: str, port: int, path: str, timeout_s: float) -> dict[str, Any]:
    start = time.perf_counter()
    http_method = "HEAD" if method == "http_head" else "GET"
    try:
        conn = http.client.HTTPConnection(target, port, timeout=timeout_s)
        conn.request(http_method, path)
        resp = conn.getresponse()
        resp.read(1024)
        conn.close()
        return {
            "status": "http_response",
            "http_status": resp.status,
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "http_error",
            "http_status": None,
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "error": type(exc).__name__,
        }


def scan_request(scope_path: str | Path | None, request: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()

    base = {
        "schema_version": SCHEMA_VERSION,
        "decision": BLOCKED,
        "reason": None,
        "network_attempted": False,
        "target": request.get("target"),
        "port": request.get("port"),
        "method": request.get("method"),
        "result": None,
        "latency_ms": 0,
    }

    if scope_path is None:
        base["reason"] = "missing_scope_artifact"
        return base

    try:
        scope = load_scope(scope_path)
    except Exception as exc:
        base["reason"] = f"scope_load_failed:{type(exc).__name__}"
        return base

    auth = authorize_request(scope, request)
    if not auth["allowed"]:
        base["reason"] = auth["reason"]
        return base

    target = str(request["target"])
    port = int(request["port"])
    method = str(request["method"])
    path = str(request.get("path", "/"))
    timeout_s = float(request.get("timeout_s", 1.0))
    if timeout_s <= 0 or timeout_s > 5:
        base["reason"] = "timeout_out_of_bounds"
        return base

    base["decision"] = ALLOWED
    base["reason"] = "request_in_scope"
    base["network_attempted"] = True

    if method == "tcp_connect":
        base["result"] = tcp_connect(target, port, timeout_s)
    elif method in {"http_head", "http_get"}:
        base["result"] = http_health(method, target, port, path, timeout_s)
    else:
        base["decision"] = BLOCKED
        base["reason"] = "unsupported_method"
        base["network_attempted"] = False
        base["result"] = None

    base["latency_ms"] = int((time.perf_counter() - started) * 1000)
    return base


def run_file(scope_path: str | Path | None, request_path: str | Path, out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    request = _read_json(request_path)
    result = scan_request(scope_path, request)

    _write_json(out / "network.scan.json", result)

    report = [
        "# Network Active Scan With Scope",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Reason: `{result['reason']}`",
        f"- Network attempted: `{result['network_attempted']}`",
        f"- Target: `{result['target']}`",
        f"- Port: `{result['port']}`",
        f"- Method: `{result['method']}`",
        f"- Latency ms: `{result['latency_ms']}`",
        "",
    ]
    if result["result"] is not None:
        report += [
            "## Result",
            "",
            "```json",
            json.dumps(result["result"], indent=2, sort_keys=True),
            "```",
            "",
        ]

    (out / "network.report.md").write_text("\n".join(report), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strictly scoped active network scan.")
    parser.add_argument("--scope", required=False, default="")
    parser.add_argument("--request", required=True)
    parser.add_argument("--out", default=".aapp/network-scan")
    args = parser.parse_args(argv)

    scope = args.scope if args.scope else None
    result = run_file(scope, args.request, args.out)

    print(
        "AAPP network active scan complete: "
        f"decision={result['decision']} "
        f"reason={result['reason']} "
        f"network_attempted={result['network_attempted']} "
        f"out={Path(args.out).resolve()}"
    )
    return 0 if result["decision"] == ALLOWED else 1


if __name__ == "__main__":
    raise SystemExit(main())
