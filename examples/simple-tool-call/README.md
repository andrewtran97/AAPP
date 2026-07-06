# Simple Tool Call Demo

This example demonstrates a local AAPP evidence chain.

Commands:

    python3 -m aapp.cli demo --out evidence/demo
    python3 -m aapp.cli verify evidence/demo/trace.jsonl --key-file evidence/demo/dev.key
    python3 -m aapp.cli report evidence/demo/trace.jsonl --out evidence/demo/evidence.report.md

Expected verify result:

    PASS: action chain verified

Tamper test:

Edit one byte in evidence/demo/trace.jsonl, then run verify again.

Expected tamper result:

    FAIL: action chain verification failed
