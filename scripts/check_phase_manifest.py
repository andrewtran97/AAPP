#!/usr/bin/env python3
from pathlib import Path
import os
import re

PHASE_DIR = Path("docs/phase-notes")
STANDARD_PATH = Path("docs/PHASE_MANIFEST_STANDARD.md")

REQUIRED_STANDARD_SECTIONS = [
    "## Required Template",
    "## Global Rules",
    "## 1. Phase Name & ID",
    "## 2. Objective / Goal",
    "## 3. Problem Statement",
    "## 4. Scope",
    "### In Scope",
    "### Out of Scope / Non-Goals",
    "### Future Considerations",
    "## 5. Metrics",
    "### Completion Metrics / Definition of Done",
    "### Quality & Safety Metrics",
    "### Adoption / Usability Metrics",
    "### Performance / Scale Metrics",
    "## 6. Deliverables",
    "### Required Files",
    "### Code Artifacts",
    "### Documentation",
    "### Machine-Readable Outputs",
    "## 7. Dependencies & Prerequisites",
    "## 8. Key Design Decisions",
    "## 9. Validation Strategy",
    "### Automated Validation",
    "### Manual Validation",
    "### Scenario Validation",
    "### Review Process",
    "## 10. Risks & Mitigations",
    "## 11. Kill Conditions",
    "## 12. Success Criteria",
    "## 13. Transition to Next Phase",
    "## 14. Timeline & Owner",
]

FULL_MANIFEST_SECTIONS = [
    "## 1. Phase Name & ID",
    "## 2. Objective / Goal",
    "## 3. Problem Statement",
    "## 4. Scope",
    "### In Scope",
    "### Out of Scope / Non-Goals",
    "### Future Considerations",
    "## 5. Metrics",
    "### Completion Metrics / Definition of Done",
    "### Quality & Safety Metrics",
    "### Adoption / Usability Metrics",
    "### Performance / Scale Metrics",
    "## 6. Deliverables",
    "### Required Files",
    "### Code Artifacts",
    "### Documentation",
    "### Machine-Readable Outputs",
    "## 7. Dependencies & Prerequisites",
    "## 8. Key Design Decisions",
    "## 9. Validation Strategy",
    "### Automated Validation",
    "### Manual Validation",
    "### Scenario Validation",
    "### Review Process",
    "## 10. Risks & Mitigations",
    "## 11. Kill Conditions",
    "## 12. Success Criteria",
    "## 13. Transition to Next Phase",
    "## 14. Timeline & Owner",
]

STALE_B28_PHRASE = "B28 Threat Detection Signals"

def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def check_standard() -> list[str]:
    failures = []

    if not STANDARD_PATH.exists():
        return [f"missing {STANDARD_PATH}"]

    text = read(STANDARD_PATH)

    for section in REQUIRED_STANDARD_SECTIONS:
        if section not in text:
            failures.append(f"{STANDARD_PATH}: missing {section}")

    return failures

def check_legacy_phase_notes() -> list[str]:
    failures = []

    if not PHASE_DIR.exists():
        return ["missing docs/phase-notes"]

    for n in range(0, 28):
        path = PHASE_DIR / f"B{n}_SCOPE.md"

        if not path.exists():
            failures.append(f"missing {path}")
            continue

        text = read(path)
        first_lines = "\n".join(text.splitlines()[:5])

        if not text.strip():
            failures.append(f"{path}: empty file")
            continue

        if f"B{n}" not in first_lines:
            failures.append(f"{path}: first lines do not identify B{n}")

    return failures

def check_stale_b28_title() -> list[str]:
    failures = []

    roots = [
        Path("docs"),
        Path("README.md"),
        Path(".github"),
        Path("scripts"),
    ]

    for root in roots:
        if root.is_file():
            paths = [root]
        elif root.is_dir():
            paths = [p for p in root.rglob("*") if p.is_file()]
        else:
            paths = []

        for path in paths:
            if "__pycache__" in path.parts:
                continue

            text = read(path)
            if STALE_B28_PHRASE in text:
                failures.append(f"{path}: stale B28 title found")

    return failures

def phase_number(path: Path) -> int | None:
    match = re.match(r"B(\d+)_SCOPE\.md$", path.name)
    if not match:
        return None
    return int(match.group(1))

def check_strict_manifests() -> list[str]:
    """
    Strict mode is opt-in.

    Reason:
    B0-B27 are historical backfill records. B27B must not rewrite all historical
    docs just to satisfy a checker introduced later.

    Enable with:
    AAPP_STRICT_PHASE_MANIFEST=1 python3 scripts/check_phase_manifest.py
    """
    failures = []

    if os.environ.get("AAPP_STRICT_PHASE_MANIFEST") != "1":
        return failures

    for path in sorted(PHASE_DIR.glob("B*_SCOPE.md")):
        n = phase_number(path)

        # B0-B27 remain legacy historical records.
        if n is not None and n <= 27:
            continue

        # B28 may exist as draft before implementation; strict mode checks it.
        text = read(path)
        missing = [section for section in FULL_MANIFEST_SECTIONS if section not in text]

        for section in missing:
            failures.append(f"{path}: missing {section}")

    return failures

def main() -> int:
    failures = []
    failures.extend(check_standard())
    failures.extend(check_legacy_phase_notes())
    failures.extend(check_stale_b28_title())
    failures.extend(check_strict_manifests())

    if failures:
        print("FAIL: phase manifest check failed")
        for item in failures:
            print(f" - {item}")
        return 1

    print("PASS: phase manifest baseline is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
