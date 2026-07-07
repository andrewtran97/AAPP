#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(".")
PHASE_DIR = ROOT / "docs" / "phase-notes"

REQUIRED_SECTIONS = [
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

def main() -> int:
    if not PHASE_DIR.exists():
        print("FAIL: docs/phase-notes missing")
        return 1

    failures = []
    for path in sorted(PHASE_DIR.glob("B*_SCOPE.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = [s for s in REQUIRED_SECTIONS if s not in text]
        if missing:
            failures.append((path, missing))

    if failures:
        print("FAIL: phase manifest section check failed")
        for path, missing in failures:
            print(path)
            for section in missing:
                print(f"  - missing: {section}")
        return 1

    print("PASS: phase manifests include required sections")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
