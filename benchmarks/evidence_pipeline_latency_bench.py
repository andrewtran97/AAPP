#!/usr/bin/env python3
"""Local B29 evidence pipeline latency benchmark.

This benchmark is local-only. It does not write runtime evidence, call the
network, call external commands, or claim production performance.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path


def load_records(path):
    records = []
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank line at {lineno}")
        records.append(json.loads(line))
    if not records:
        raise ValueError("fixture contains no records")
    return records


def canonical_bytes(record):
    return json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest_record(record):
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def run_benchmark(records, iterations):
    if iterations < 1:
        raise ValueError("iterations must be >= 1")

    durations = []
    digest_count = 0

    for _ in range(iterations):
        start = time.perf_counter()
        for record in records:
            digest_record(record)
            digest_count += 1
        durations.append(time.perf_counter() - start)

    total_seconds = sum(durations)
    records_processed = len(records) * iterations

    return {
        "record_count": len(records),
        "iterations": iterations,
        "total_seconds": total_seconds,
        "records_per_second": records_processed / total_seconds if total_seconds else 0.0,
        "min_seconds": min(durations),
        "max_seconds": max(durations),
        "avg_seconds": total_seconds / iterations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture",
        default="tests/fixtures/evidence_performance/sample_records.jsonl",
    )
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()

    records = load_records(args.fixture)
    result = run_benchmark(records, args.iterations)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
