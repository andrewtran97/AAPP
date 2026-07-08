#!/usr/bin/env python3
from pathlib import Path

PUBLIC_ROOTS = [
    Path("README.md"),
    Path("docs"),
    Path(".github"),
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
    "not a",
    "no ",
    "without claiming",
    "does not provide",
    "must not claim",
    "claim restrictions",
]

SKIP_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
}

def iter_files():
    for root in PUBLIC_ROOTS:
        if root.is_file():
            yield root
            continue

        if not root.is_dir():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            yield path

def is_guarded(lines, index):
    start = max(0, index - 30)
    end = min(len(lines), index + 2)
    context = "\n".join(lines[start:end]).lower()
    return any(guard in context for guard in GUARD_WORDS)

def main() -> int:
    hits = []

    for path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for i, line in enumerate(lines):
            low = line.lower()
            for phrase in BAD_PHRASES:
                if phrase.lower() in low and not is_guarded(lines, i):
                    hits.append(f"{path}:{i + 1}: {line}")

    if hits:
        print("FAIL: unguarded forbidden claim language found")
        for hit in hits:
            print(hit)
        return 1

    print("PASS: claim boundary check")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
