"""Deterministic risk signal generation for B28."""


def generate_risk_signals(record):
    """Generate deterministic risk signals from explicit input fields."""
    signals = []
    reason_codes = []

    events = record.get("events") or []
    deny_count = sum(1 for event in events if event.get("verdict") == "DENY")
    if deny_count >= 3:
        signals.append("SIGNAL_REPEATED_DENY")
        reason_codes.append("REPEATED_DENY")

    previous = record.get("previous") or {}
    current = record.get("current") or {}
    if previous.get("risk_class") == "LOW" and current.get("risk_class") == "DESTRUCTIVE":
        signals.append("SIGNAL_RISK_ESCALATION")
        reason_codes.append("LOW_TO_DESTRUCTIVE")

    context = record.get("context") or {}
    if context.get("data_class") == "restricted" and context.get("sink") == "external":
        signals.append("SIGNAL_DATA_EGRESS_RISK")
        reason_codes.append("RESTRICTED_DATA_EXTERNAL_SINK")

    return {
        "signals": signals,
        "reason_codes": reason_codes,
    }
