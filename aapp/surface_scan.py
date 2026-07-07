from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

SCHEMA_VERSION = "aapp.surface_scan.v1"

EXCLUDE_DIRS = {
    ".git", ".aapp", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", "venv", "dist", "build",
}

INTERESTING_SUFFIXES = {".yml", ".yaml", ".json", ".sh", ".py", ".rb", ".toml", ".ini", ".cfg", ".md"}

PATTERNS = {
    "network_call": {
        "curl": r"\bcurl\b",
        "wget": r"\bwget\b",
        "nc": r"\bnc\b|\bnetcat\b",
        "nmap": r"\bnmap\b",
        "tshark": r"\btshark\b",
        "ssh": r"\bssh\b",
        "scp": r"\bscp\b",
        "http_clients": r"Net::HTTP|HTTParty|Faraday|requests\.|urllib\.request|httpx\.",
    },
    "cloud_or_stateful_command": {
        "aws": r"\baws\b",
        "gcloud": r"\bgcloud\b",
        "az": r"\baz\b",
        "gh_mutation": r"\bgh\s+(api|repo|pr|issue|release|workflow|secret)\b",
        "kubectl": r"\bkubectl\b",
        "terraform": r"\bterraform\s+(apply|destroy|import|state|taint)\b",
        "psql": r"\bpsql\b",
        "mysql": r"\bmysql\b",
        "stripe": r"\bstripe\b",
    },
    "shell_execution": {
        "python_subprocess": r"\bsubprocess\.",
        "python_os_system": r"\bos\.system\s*\(",
        "ruby_open3": r"\bOpen3\b",
        "ruby_iopopen": r"\bIO\.popen\b",
        "ruby_system": r"\bsystem\s*\(",
        "workflow_run_block": r"\brun:\s*\|",
    },
    "secret_reference": {
        "github_secrets_context": r"\$\{\{\s*secrets\.",
        "github_token": r"\bGITHUB_TOKEN\b",
        "env_secret": r"\bENV\[['\"][A-Z0-9_]*(TOKEN|KEY|SECRET|PASSWORD)[A-Z0-9_]*['\"]\]",
        "secret_word": r"\b(API_KEY|ACCESS_KEY|SECRET|PASSWORD|TOKEN)\b",
    },
    "stateful_write": {
        "file_write": r"\b(File\.write|open\(.+['\"]w|write_text|write_bytes|echo\s+.+>|tee\s+)",
        "rm_rf": r"\brm\s+-rf\b",
        "db_mutation": r"\b(UPDATE|DELETE\s+FROM|INSERT\s+INTO|DROP\s+TABLE)\b",
    },
}

EVIDENCE_HINT = re.compile(r"(agent_blackbox|aapp|evidence|session_bundle|mcp_proxy_recorder)", re.I)
REVERSAL_HINT = re.compile(r"(rollback|reversal|restore|backup|undo|compensat)", re.I)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _line(text: str, pattern: str) -> int:
    rx = re.compile(pattern, re.I | re.M)
    for i, line in enumerate(text.splitlines(), start=1):
        if rx.search(line):
            return i
    return 1


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


def _severity(surface_type: str, evidence_gap: bool, reversal_gap: bool) -> str:
    if surface_type in {"github_workflow", "cloud_or_stateful_command", "stateful_write"} and (evidence_gap or reversal_gap):
        return "HIGH"
    if surface_type in {"network_call", "shell_execution", "ruby_security_tooling"} and evidence_gap:
        return "MEDIUM"
    return "LOW"


def _next_action(surface_type: str, severity: str) -> str:
    if severity == "HIGH":
        return "Add evidence capture and a reversal/rollback note before this path is trusted."
    if surface_type == "secret_reference":
        return "Record only secret references/digests; never write raw secret values to reports."
    if surface_type == "network_call":
        return "Add scope evidence and request/response digest capture; do not store raw sensitive payloads."
    return "Review whether this surface needs evidence capture or an explicit low-risk waiver."


def _finding(surface_type: str, detector: str, rel: str, line: int, evidence_gap: bool, reversal_gap: bool) -> dict:
    severity = _severity(surface_type, evidence_gap, reversal_gap)
    return {
        "rule_id": f"AAPP-SURFACE-{surface_type.upper().replace('_', '-')}",
        "severity": severity,
        "file_path": rel,
        "line_hint": line,
        "surface_type": surface_type,
        "rationale": f"{surface_type} detected by {detector}; evidence_gap={evidence_gap}; reversal_gap={reversal_gap}.",
        "evidence_gap": evidence_gap,
        "reversal_gap": reversal_gap,
        "next_action": _next_action(surface_type, severity),
    }


def _sarif(findings: list[dict]) -> dict:
    rules = {}
    results = []
    for f in findings:
        level = "error" if f["severity"] == "HIGH" else "warning" if f["severity"] == "MEDIUM" else "note"
        rules.setdefault(f["rule_id"], {
            "id": f["rule_id"],
            "shortDescription": {"text": f["surface_type"]},
            "fullDescription": {"text": f["rationale"]},
            "defaultConfiguration": {"level": level},
        })
        results.append({
            "ruleId": f["rule_id"],
            "level": level,
            "message": {"text": f"{f['rationale']} Next action: {f['next_action']}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f["file_path"]},
                    "region": {"startLine": max(1, int(f["line_hint"]))},
                }
            }],
        })
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {
                "name": "Agent Black Box Surface Scan",
                "informationUri": "https://github.com/andrewtran97/AAPP",
                "rules": list(rules.values()),
            }},
            "results": results,
        }],
    }


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scan_repo(repo: str | Path, out: str | Path) -> dict:
    start = time.perf_counter()
    repo = Path(repo).resolve()
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    surfaces = []
    findings = []
    files_scanned = workflows_scanned = scripts_scanned = 0

    for path in _iter_files(repo):
        files_scanned += 1
        rel = path.relative_to(repo).as_posix()
        text = _read(path)
        suffix = path.suffix.lower()

        if rel.startswith(".github/workflows/"):
            workflows_scanned += 1
        if suffix in {".sh", ".py", ".rb"}:
            scripts_scanned += 1

        evidence_gap = not bool(EVIDENCE_HINT.search(text))
        reversal_gap = not bool(REVERSAL_HINT.search(text))
        hits: list[tuple[str, str, int]] = []

        if rel.startswith(".github/workflows/"):
            hits.append(("github_workflow", "github_workflow", 1))
        if suffix == ".rb":
            hits.append(("ruby_security_tooling", "ruby_file", 1))

        for surface_type, detectors in PATTERNS.items():
            for detector, pattern in detectors.items():
                if re.search(pattern, text, re.I | re.M):
                    hits.append((surface_type, detector, _line(text, pattern)))

        seen = set()
        for surface_type, detector, line in hits:
            key = (surface_type, detector, line)
            if key in seen:
                continue
            seen.add(key)
            surfaces.append({
                "surface_id": f"SURF-{len(surfaces)+1:04d}",
                "file_path": rel,
                "line_hint": line,
                "surface_type": surface_type,
                "detector": detector,
                "evidence": f"sha256:{_sha(rel + ':' + detector)[:16]}",
            })
            findings.append(_finding(surface_type, detector, rel, line, evidence_gap, reversal_gap))

    high = sum(1 for f in findings if f["severity"] == "HIGH")
    medium = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low = sum(1 for f in findings if f["severity"] == "LOW")
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "repos_scanned": 1,
        "files_scanned": files_scanned,
        "workflows_scanned": workflows_scanned,
        "scripts_scanned": scripts_scanned,
        "surfaces_detected": len(surfaces),
        "high_findings": high,
        "medium_findings": medium,
        "low_findings": low,
        "evidence_gaps": sum(1 for f in findings if f["evidence_gap"]),
        "posture_gaps": sum(1 for f in findings if f["reversal_gap"]),
        "scan_duration_ms": int((time.perf_counter() - start) * 1000),
    }

    surface_map = {"schema_version": SCHEMA_VERSION, "repo": str(repo), "surfaces": surfaces}
    risk_findings = {"schema_version": SCHEMA_VERSION, "findings": findings}
    evidence_gap = {"schema_version": SCHEMA_VERSION, "gaps": [f for f in findings if f["evidence_gap"]]}

    lines = [
        "# Agent Action Surface Scan",
        "",
        f"- Repo: `{repo}`",
        f"- Files scanned: {files_scanned}",
        f"- Surfaces detected: {len(surfaces)}",
        f"- HIGH: {high}",
        f"- MEDIUM: {medium}",
        f"- LOW: {low}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No agent action surfaces detected by B15 rules.")
    for f in findings:
        lines += [
            f"### {f['severity']}: {f['surface_type']}",
            "",
            f"- Rule: `{f['rule_id']}`",
            f"- Path: `{f['file_path']}:{f['line_hint']}`",
            f"- Rationale: {f['rationale']}",
            f"- Next action: {f['next_action']}",
            "",
        ]

    _write_json(out / "surface.map.json", surface_map)
    _write_json(out / "risk_findings.json", risk_findings)
    _write_json(out / "evidence_gap.json", evidence_gap)
    _write_json(out / "surface.metrics.json", metrics)
    _write_json(out / "surface.sarif.json", _sarif(findings))
    (out / "surface.report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "surface_map": surface_map,
        "risk_findings": risk_findings,
        "evidence_gap": evidence_gap,
        "metrics": metrics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a repo for AI agent action surfaces.")
    parser.add_argument("--repo", default=".", help="Repository path to scan.")
    parser.add_argument("--out", default=".aapp/surface-scan", help="Output directory.")
    args = parser.parse_args(argv)
    result = scan_repo(args.repo, args.out)
    m = result["metrics"]
    print(
        "AAPP surface scan complete: "
        f"surfaces={m['surfaces_detected']} "
        f"high={m['high_findings']} "
        f"medium={m['medium_findings']} "
        f"low={m['low_findings']} "
        f"out={Path(args.out).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
