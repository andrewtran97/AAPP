"""Deterministic policy abstraction for B28."""

TOOL_ACTIONS = {
    "read_file": "read",
    "write_file": "write",
}


def abstract_policy(raw):
    """Convert a raw tool-call record into a deterministic policy abstraction."""
    subject = raw.get("subject", "unknown")
    tool = raw.get("tool", "unknown")
    resource = raw.get("resource", "unknown")
    params = raw.get("params") or {}

    action = TOOL_ACTIONS.get(tool, "unknown")

    context = {"tool": tool}
    if "mode" in params:
        context["mode"] = params["mode"]
    if "destructive" in params:
        context["destructive"] = params["destructive"]

    if action == "read":
        return {
            "subject": subject,
            "action": action,
            "resource": resource,
            "context": context,
            "risk_class": "LOW",
            "obligations": [],
            "reason_codes": ["ACTION_READ"],
        }

    if action == "write" and params.get("destructive") is True:
        return {
            "subject": subject,
            "action": action,
            "resource": resource,
            "context": context,
            "risk_class": "DESTRUCTIVE",
            "obligations": ["require_approval", "require_reversal_plan"],
            "reason_codes": ["ACTION_WRITE", "DESTRUCTIVE_ACTION"],
        }

    return {
        "subject": subject,
        "action": "unknown",
        "resource": resource,
        "context": context,
        "risk_class": "UNKNOWN",
        "obligations": ["require_review"],
        "reason_codes": ["UNKNOWN_ACTION"],
    }
