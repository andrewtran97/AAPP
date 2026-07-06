#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


SHA_RE = re.compile(r"^[a-fA-F0-9]{40}$")
USES_RE = re.compile(r"uses:\s*['\"]?([^'\"\s#]+)")
RUN_RE = re.compile(r"^\s*run:\s*(\||>|.*)$")


def workflow_files() -> List[Path]:
    if not WORKFLOWS.is_dir():
        return []
    return sorted(
        p for p in WORKFLOWS.iterdir()
        if p.suffix in {".yml", ".yaml"} and p.is_file()
    )


def is_full_sha_ref(value: str) -> bool:
    if "@" not in value:
        return False
    ref = value.rsplit("@", 1)[1]
    return bool(SHA_RE.match(ref))


def extract_uses(lines: Iterable[str]) -> List[str]:
    found = []
    for line in lines:
        m = USES_RE.search(line)
        if m:
            found.append(m.group(1))
    return found


def audit_workflow(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: List[str] = []

    has_permissions = bool(re.search(r"(?m)^permissions:\s*$", text))
    if has_permissions:
        findings.append(f"PASS: {path}: top-level permissions block present")
    else:
        findings.append(f"WARN: {path}: no top-level permissions block found")

    if "pull_request_target:" in text:
        findings.append(f"WARN: {path}: uses pull_request_target; review privileged context and untrusted checkout")
    else:
        findings.append(f"PASS: {path}: no pull_request_target trigger found")

    if "workflow_run:" in text:
        findings.append(f"WARN: {path}: uses workflow_run; review artifact trust boundary")
    else:
        findings.append(f"PASS: {path}: no workflow_run trigger found")

    uses = extract_uses(lines)
    if not uses:
        findings.append(f"PASS: {path}: no third-party actions referenced through uses")
    for action in uses:
        if action.startswith("./"):
            findings.append(f"PASS: {path}: local action reference {action}")
        elif is_full_sha_ref(action):
            findings.append(f"PASS: {path}: action pinned to full SHA: {action}")
        else:
            findings.append(f"NOTE: {path}: action not pinned to full SHA: {action}")

    if "upload-artifact" in text or "download-artifact" in text:
        findings.append(f"NOTE: {path}: artifact action present; review retention/provenance/consumer trust")
    else:
        findings.append(f"PASS: {path}: no artifact upload/download action found")

    risky_context_lines = []
    for idx, line in enumerate(lines, start=1):
        if "github.event." in line and ("run:" in line or "${{" in line):
            risky_context_lines.append(idx)

    if risky_context_lines:
        findings.append(f"NOTE: {path}: github.event context appears near shell/evaluation lines {risky_context_lines}")
    else:
        findings.append(f"PASS: {path}: no obvious github.event shell interpolation found")

    return findings


def build_report() -> str:
    files = workflow_files()
    lines = [
        "# GitHub Actions Boundary Audit",
        "",
        "This report reviews AAPP workflow permission, trigger, action pinning, artifact, and untrusted-input boundaries.",
        "",
        "This is a static review helper. It does not prove absence of vulnerability.",
        "",
        "## Workflow files",
        "",
    ]

    if not files:
        lines.append("- No workflow files found")
    else:
        for p in files:
            lines.append(f"- `{p.relative_to(ROOT)}`")

    lines.extend(["", "## Findings", ""])

    for p in files:
        lines.append(f"### `{p.relative_to(ROOT)}`")
        lines.append("")
        for finding in audit_workflow(p):
            lines.append(f"- {finding}")
        lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "- PASS: expected boundary is present or no risky construct found.",
        "- NOTE: not automatically unsafe; needs human review.",
        "- WARN: privileged or missing-boundary pattern requiring explicit review.",
        "",
        "## Kill conditions",
        "",
        "- Do not weaken branch protection.",
        "- Do not add secrets to workflows.",
        "- Do not use public issues for security details.",
        "- Do not claim an advisory without a real, reproducible vulnerability.",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    print(build_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
