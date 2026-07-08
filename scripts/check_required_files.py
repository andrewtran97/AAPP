#!/usr/bin/env python3
from pathlib import Path

REQUIRED = [
    "docs/PHASE_MANIFEST_STANDARD.md",
    "docs/ROADMAP_CANONICAL.md",
    "docs/ARCHITECTURE.md",
    "docs/TERMINOLOGY.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/phase.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "scripts/check_phase_manifest.py",
    "scripts/check_claim_boundaries.py",
    "scripts/check_required_files.py",
]

def main() -> int:
    missing = [p for p in REQUIRED if not Path(p).exists()]

    for n in range(0, 28):
        p = f"docs/phase-notes/B{n}_SCOPE.md"
        if not Path(p).exists():
            missing.append(p)

    if missing:
        print("FAIL: missing required files")
        for p in missing:
            print(f" - {p}")
        return 1

    print("PASS: required files exist")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
