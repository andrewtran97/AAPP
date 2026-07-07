from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "aapp.network_scope.v1"

ALLOWED_METHODS = {"tcp_connect", "http_head", "http_get"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp_invalid")
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp_missing_timezone")
    return parsed.astimezone(timezone.utc)


def load_scope(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise ValueError("missing_scope_artifact")
    scope = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(scope, dict):
        raise ValueError("scope_not_object")
    return scope


def validate_scope(scope: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or utc_now()

    if scope.get("schema_version") != SCHEMA_VERSION:
        return {"allowed": False, "reason": "unsupported_scope_schema"}

    required = [
        "scope_id",
        "authorized_by",
        "created_at",
        "expires_at",
        "allowed_targets",
        "allowed_ports",
        "allowed_methods",
        "rate_limit",
        "purpose",
        "no_exploit",
    ]
    for key in required:
        if key not in scope:
            return {"allowed": False, "reason": f"missing_scope_field:{key}"}

    if scope.get("no_exploit") is not True:
        return {"allowed": False, "reason": "no_exploit_not_true"}

    try:
        expires_at = parse_time(scope["expires_at"])
    except Exception:
        return {"allowed": False, "reason": "expires_at_invalid"}

    if expires_at <= now:
        return {"allowed": False, "reason": "scope_expired"}

    if not isinstance(scope.get("allowed_targets"), list) or not scope["allowed_targets"]:
        return {"allowed": False, "reason": "allowed_targets_invalid"}
    if not isinstance(scope.get("allowed_ports"), list) or not scope["allowed_ports"]:
        return {"allowed": False, "reason": "allowed_ports_invalid"}
    if not isinstance(scope.get("allowed_methods"), list) or not scope["allowed_methods"]:
        return {"allowed": False, "reason": "allowed_methods_invalid"}

    for method in scope["allowed_methods"]:
        if method not in ALLOWED_METHODS:
            return {"allowed": False, "reason": f"unsupported_scope_method:{method}"}

    for target in scope["allowed_targets"]:
        if not isinstance(target, str) or not target:
            return {"allowed": False, "reason": "allowed_target_invalid"}
        if "*" in target or "/" in target:
            return {"allowed": False, "reason": "wildcard_or_cidr_not_supported_in_mvp"}

    for port in scope["allowed_ports"]:
        if not isinstance(port, int) or port < 1 or port > 65535:
            return {"allowed": False, "reason": "allowed_port_invalid"}

    rate_limit = scope.get("rate_limit")
    if not isinstance(rate_limit, dict):
        return {"allowed": False, "reason": "rate_limit_invalid"}

    max_attempts = rate_limit.get("max_attempts")
    if not isinstance(max_attempts, int) or max_attempts < 1 or max_attempts > 100:
        return {"allowed": False, "reason": "rate_limit_max_attempts_invalid"}

    return {"allowed": True, "reason": "scope_valid"}


def authorize_request(scope: dict[str, Any], request: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    scope_result = validate_scope(scope, now=now)
    if not scope_result["allowed"]:
        return {"allowed": False, "reason": scope_result["reason"]}

    target = request.get("target")
    port = request.get("port")
    method = request.get("method")

    if target not in scope["allowed_targets"]:
        return {"allowed": False, "reason": "target_not_in_scope"}
    if port not in scope["allowed_ports"]:
        return {"allowed": False, "reason": "port_not_in_scope"}
    if method not in scope["allowed_methods"]:
        return {"allowed": False, "reason": "method_not_in_scope"}

    if request.get("exploit") is True or request.get("fuzz") is True or request.get("credential_attack") is True:
        return {"allowed": False, "reason": "prohibited_mode_requested"}

    return {"allowed": True, "reason": "request_in_scope"}
