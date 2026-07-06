"""Scope gate for AAPP active recording."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ScopeError(ValueError):
    """Raised when an AAPP operation is outside authorized scope."""


REQUIRED_SCOPE_FIELDS = {
    "schema_version",
    "scope_id",
    "authorization_status",
    "allowed_actor_types",
    "allowed_tool_types",
    "active_operations_enabled",
}


def load_scope(path: str | Path) -> Dict[str, Any]:
    scope_path = Path(path)

    if not scope_path.exists():
        raise ScopeError(f"scope file does not exist: {scope_path}")

    try:
        value = json.loads(scope_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScopeError(f"invalid scope JSON: {exc}") from exc

    if not isinstance(value, dict):
        raise ScopeError("scope file must contain a JSON object")

    return value


def validate_scope(scope: Dict[str, Any]) -> None:
    missing = sorted(REQUIRED_SCOPE_FIELDS - set(scope.keys()))
    if missing:
        raise ScopeError(f"scope missing required fields: {', '.join(missing)}")

    if scope["schema_version"] != "0.1.0":
        raise ScopeError("unsupported scope schema_version")

    if scope["authorization_status"] != "authorized":
        raise ScopeError("scope is not authorized")

    if scope["active_operations_enabled"] is not True:
        raise ScopeError("active operations are disabled by scope")

    if not isinstance(scope["allowed_actor_types"], list) or not scope["allowed_actor_types"]:
        raise ScopeError("allowed_actor_types must be a non-empty list")

    if not isinstance(scope["allowed_tool_types"], list) or not scope["allowed_tool_types"]:
        raise ScopeError("allowed_tool_types must be a non-empty list")


def require_authorized_scope(
    *,
    scope: Dict[str, Any],
    actor_type: str,
    tool_type: str,
) -> None:
    validate_scope(scope)

    if actor_type not in scope["allowed_actor_types"]:
        raise ScopeError(f"actor_type not authorized: {actor_type}")

    if tool_type not in scope["allowed_tool_types"]:
        raise ScopeError(f"tool_type not authorized: {tool_type}")


def scope_id(scope: Dict[str, Any]) -> str:
    validate_scope(scope)
    return str(scope["scope_id"])
