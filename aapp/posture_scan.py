from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

SCHEMA_VERSION = "aapp.posture_scan.v1"

EXCLUDE_DIRS = {
    ".git", ".aapp", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", "venv", "dist", "build",
}

INTERESTING_SUFFIXES = {".yml", ".yaml", ".json", ".sh", ".py", ".rb", ".toml", ".ini", ".cfg", ".md"}

PERMISSION_PATTERNS = {
    "permissions_write_all": r"(?m)^\s*permissions\s*:\s*write-all\s*$",
    "contents_write": r"(?m)^\s*contents\s*:\s*write\s*$",
    "actions_write": r"(?m)^\s*actions\s*:\s*write\s*$",
    "packages_write": r"(?m)^\s*packages\s*:\s*write\s*$",
    "checks_write": r"(?m)^\s*checks\s*:\s*write\s*$",
    "deployments_write": r"(?m)^\s*deployments\s*:\s*write\s*$",
    "id_token_write": r"(?m)^\s*id-token\s*:\s*write\s*$",
    "security_events_write": r"(?m)^\s*security-events\s*:\s*write\s*$",
}

SECRET_PATTERNS = {
    "github_secrets_context": r"\$\{\{\s*secrets\.",
    "github_token": r"\bGITHUB_TOKEN\b",
    "aws_access_key": r"\bAWS_ACCESS_KEY_ID\b|\bAWS_SECRET_ACCESS_KEY\b",
    "gcp_credentials": r"\bGOOGLE_APPLICATION_CREDENTIALS\b|\bGCP_SERVICE_ACCOUNT\b|\bGCP_SA_KEY\b",
    "azure_credentials": r"\bAZURE_CREDENTIALS\b|\bAZURE_CLIENT_SECRET\b",
    "generic_service_account": r"\bSERVICE_ACCOUNT\b|\bSERVICE_ACCOUNT_KEY\b",
    "token_env": r"\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[A-Z0-9_]*\b",
}

STATEFUL_PATTERNS = {
    "terraform_apply": r"\bterraform\s+(apply|destroy|import|state|taint)\b",
    "kubectl_mutation": r"\bkubectl\s+(apply|delete|patch|replace|scale|rollout|create)\b",
    "aws_mutation": r"\baws\s+([a-z0-9-]+\s+)?(put|create|delete|update|attach|detach|copy|cp|sync|deploy)\b",
    "gh_mutation": r"\bgh\s+(api|repo|pr|issue|release|workflow|secret)\b",
    "db_mutation": r"\b(UPDATE|DELETE\s+FROM|INSERT\s+INTO|DROP\s+TABLE|ALTER\s+TABLE)\b",
    "stripe_mutation": r"\bstripe\b",
    "docker_push": r"\bdocker\s+(push|buildx\s+build)\b",
    "file_delete": r"\brm\s+-rf\b",
    "file_write": r"\b(File\.write|write_text|write_bytes|tee\s+|echo\s+.+>)",
}

CI_AGENT_PATH_PATTERNS = {
    "runs_script": r"(?m)^\s*run\s*:\s*(ruby|python|bash|sh|\./|scripts/)",
    "run_block": r"(?m)^\s*run\s*:\s*\|",
    "mcp_ref": r"\bmcp\b|\btools/call\b",
    "agent_ref": r"\bagent\b|agentic|autonomous",
}

ROLLBACK_HINT = re.compile(r"(rollback|reversal|restore|backup|undo|compensat)", re.I)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _iter_files(repo: Path):
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        rel = path.relative_to(repo).as_posix()
        if rel.startswith(".github/workflows/") or path.suffix.lower() in INTERESTING_SUFFIXES:
            yield path


def _line(text: str, pattern: str) -> int:
    rx = re.compile(pattern, re.I | re.M)
    for i, line in enumerate(text.splitlines(), start=1):
        if rx.search(line):
            return i
    return 1


def _hits(text: str, patterns: dict[str, str]) -> list[tuple[str, int]]:
    out = []
    for name, pattern in patterns.items():
        if re.search(pattern, text, re.I | re.M):
            out.append((name, _line(text, pattern)))
    return out


def _severity(permission_risk: bool, stateful_action: bool, rollback_gap: bool, secret_usage: bool) -> str:
    if permission_risk and stateful_action and rollback_gap:
        return "HIGH"
    if stateful_action and rollback_gap:
        return "HIGH"
    if permission_risk and secret_usage:
        return "HIGH"
    if permission_risk or stateful_action or secret_usage:
        return "MEDIUM"
    return "LOW"


def _next_action(posture_type: str, severity: str) -> str:
    if posture_type == "permission_risk":
        return "Reduce workflow/job permissions to least privilege and add evidence capture for this path."
    if posture_type == "secret_usage":
        return "Record only secret references/digests; never write raw secret values to reports."
    if posture_type == "stateful_action":
        return "Add state ledger capture and a reversal plan before trusting this state-changing path."
    if posture_type == "ci_runner_agent_path":
        return "Bind this CI runner path to evidence capture and posture reporting."
    if severity == "HIGH":
        return "Block rollout until evidence capture and rollback/reversal plan exist."
    return "Review posture and document why this path is low risk."


def _finding(rel: str, line: int, posture_type: str, detector: str, permission_risk: bool, stateful_action: bool, rollback_gap: bool, secret_usage: bool) -> dict:
    severity = _severity(permission_risk, stateful_action, rollback_gap, secret_usage)
    return {
        "rule_id": f"AAPP-POSTURE-{posture_type.upper().replace('_', '-')}",
        "severity": severity,
        "file_path": rel,
        "line_hint": line,
        "posture_type": posture_type,
        "detector": detector,
        "rationale": (
            f"{posture_type} detected by {detector}; "
            f"permission_risk={permission_risk}; "
            f"stateful_action={stateful_action}; "
            f"rollback_gap={rollback_gap}; "
            f"secret_usage={secret_usage}."
        ),
        "permission_risk": permission_risk,
        "stateful_action": stateful_action,
        "rollback_gap": rollback_gap,
        "next_action": _next_action(posture_type, severity),
    }


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scan_repo(repo: str | Path, out: str | Path) -> dict:
    start = time.perf_counter()
    repo = Path(repo).resolve()
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    posture_items = []
    findings = []
    stateful_actions = []
    rollback_gaps = []

    files_scanned = workflows_scanned = scripts_scanned = 0

    for path in _iter_files(repo):
        files_scanned += 1
        rel = path.relative_to(repo).as_posix()
        text = _read(path)
        suffix = path.suffix.lower()

        is_workflow = rel.startswith(".github/workflows/")
        if is_workflow:
            workflows_scanned += 1
        if suffix in {".sh", ".py", ".rb"}:
            scripts_scanned += 1

        permission_hits = _hits(text, PERMISSION_PATTERNS) if is_workflow else []
        secret_hits = _hits(text, SECRET_PATTERNS)
        stateful_hits = _hits(text, STATEFUL_PATTERNS)
        ci_path_hits = _hits(text, CI_AGENT_PATH_PATTERNS) if is_workflow or suffix in {".sh", ".py", ".rb"} else []

        has_permission_risk = bool(permission_hits)
        has_secret_usage = bool(secret_hits)
        has_stateful = bool(stateful_hits)
        has_rollback_hint = bool(ROLLBACK_HINT.search(text))
        has_rollback_gap = has_stateful and not has_rollback_hint

        file_hits: list[tuple[str, str, int]] = []
        file_hits += [("permission_risk", name, line) for name, line in permission_hits]
        file_hits += [("secret_usage", name, line) for name, line in secret_hits]
        file_hits += [("stateful_action", name, line) for name, line in stateful_hits]
        file_hits += [("ci_runner_agent_path", name, line) for name, line in ci_path_hits]

        seen = set()
        for posture_type, detector, line in file_hits:
            key = (posture_type, detector, line)
            if key in seen:
                continue
            seen.add(key)

            item = {
                "posture_id": f"POSTURE-{len(posture_items)+1:04d}",
                "file_path": rel,
                "line_hint": line,
                "posture_type": posture_type,
                "detector": detector,
                "permission_risk": has_permission_risk,
                "secret_usage": has_secret_usage,
                "stateful_action": has_stateful,
                "rollback_gap": has_rollback_gap,
            }
            posture_items.append(item)

            finding = _finding(
                rel=rel,
                line=line,
                posture_type=posture_type,
                detector=detector,
                permission_risk=has_permission_risk,
                stateful_action=has_stateful,
                rollback_gap=has_rollback_gap,
                secret_usage=has_secret_usage,
            )
            findings.append(finding)

            if posture_type == "stateful_action":
                stateful_actions.append(item)
            if has_rollback_gap and posture_type in {"stateful_action", "permission_risk", "ci_runner_agent_path"}:
                rollback_gaps.append({
                    "file_path": rel,
                    "line_hint": line,
                    "detector": detector,
                    "reason": "stateful action detected without rollback/reversal hint",
                    "next_action": "Add reversal plan or document manual-review path.",
                })

    high = sum(1 for f in findings if f["severity"] == "HIGH")
    medium = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low = sum(1 for f in findings if f["severity"] == "LOW")

    posture_map = {
        "schema_version": SCHEMA_VERSION,
        "repo": str(repo),
        "summary": {
            "files_scanned": files_scanned,
            "workflows_scanned": workflows_scanned,
            "scripts_scanned": scripts_scanned,
            "posture_items": len(posture_items),
            "high_findings": high,
            "medium_findings": medium,
            "low_findings": low,
            "scan_duration_ms": int((time.perf_counter() - start) * 1000),
        },
        "posture": posture_items,
    }

    report_lines = [
        "# Agent Posture Scan",
        "",
        f"- Repo: `{repo}`",
        f"- Files scanned: {files_scanned}",
        f"- Workflows scanned: {workflows_scanned}",
        f"- Scripts scanned: {scripts_scanned}",
        f"- Posture items: {len(posture_items)}",
        f"- HIGH: {high}",
        f"- MEDIUM: {medium}",
        f"- LOW: {low}",
        "",
        "## Findings",
        "",
    ]

    if not findings:
        report_lines.append("No posture findings detected by B16 rules.")
    for f in findings:
        report_lines += [
            f"### {f['severity']}: {f['posture_type']}",
            "",
            f"- Rule: `{f['rule_id']}`",
            f"- Path: `{f['file_path']}:{f['line_hint']}`",
            f"- Rationale: {f['rationale']}",
            f"- Next action: {f['next_action']}",
            "",
        ]

    _write_json(out / "posture.map.json", posture_map)
    _write_json(out / "posture.findings.json", {"schema_version": SCHEMA_VERSION, "findings": findings})
    _write_json(out / "stateful_actions.json", {"schema_version": SCHEMA_VERSION, "stateful_actions": stateful_actions})
    _write_json(out / "rollback_gaps.json", {"schema_version": SCHEMA_VERSION, "rollback_gaps": rollback_gaps})
    (out / "posture.report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "posture_map": posture_map,
        "posture_findings": {"schema_version": SCHEMA_VERSION, "findings": findings},
        "stateful_actions": {"schema_version": SCHEMA_VERSION, "stateful_actions": stateful_actions},
        "rollback_gaps": {"schema_version": SCHEMA_VERSION, "rollback_gaps": rollback_gaps},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a repo for AI agent posture risks.")
    parser.add_argument("--repo", default=".", help="Repository path to scan.")
    parser.add_argument("--out", default=".aapp/posture-scan", help="Output directory.")
    args = parser.parse_args(argv)
    result = scan_repo(args.repo, args.out)
    summary = result["posture_map"]["summary"]
    print(
        "AAPP posture scan complete: "
        f"items={summary['posture_items']} "
        f"high={summary['high_findings']} "
        f"medium={summary['medium_findings']} "
        f"low={summary['low_findings']} "
        f"out={Path(args.out).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
