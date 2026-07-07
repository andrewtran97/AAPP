#!/usr/bin/env python3
from pathlib import Path

ROOTS = [
    Path("README.md"),
    Path("docs"),
    Path(".github"),
    Path("scripts"),
    Path("tests"),
    Path("aapp"),
    Path("examples"),
    Path("demo"),
]

BAD_PHRASES = [
    "compliance guaranteed",
    "full containment guarantee",
    "impossible to tamper",
    "impossible to bypass",
    "military-grade",
    "federal-grade",
    "production certified",
    "world-class",
    "zero error",
    "perfect model",
    "FedRAMP authorized",
    "FIPS validated",
    "CISA approved",
    "DoD certified",
    "NASA certified",
    "Microsoft certified",
]

GUARD_WORDS = [
    "do not",
    "does not",
    "not ",
    "forbidden",
    "non-goals",
    "not claimed",
    "claim boundary",
    "does not claim",
    "forbidden public claims",
]

def iter_files():
    for root in ROOTS:
        if root.is_file():
            yield root
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.is_file():
                    yield path

def main() -> int:
    hits = []
    for path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for i, line in enumerate(lines, 1):
            low = line.lower()
            for phrase in BAD_PHRASES:
                if phrase.lower() in low and not any(g in low for g in GUARD_WORDS):
                    hits.append(f"{path}:{i}: {line}")

    if hits:
        print("FAIL: unguarded forbidden claim language found")
        for hit in hits:
            print(hit)
        return 1

    print("PASS: claim boundary check")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
