# Simple Tool Call Demo

This example demonstrates a local AAPP evidence chain with a required scope file.

Commands:

    python3 -m aapp.cli scope-check --scope examples/simple-tool-call/scope.demo.json --actor-type agent --tool-type file_read
    python3 -m aapp.cli demo --scope examples/simple-tool-call/scope.demo.json --out evidence/demo
    python3 -m aapp.cli verify evidence/demo/trace.jsonl --key-file evidence/demo/dev.key
    python3 -m aapp.cli report evidence/demo/trace.jsonl --out evidence/demo/evidence.report.md

Expected verify result:

    PASS: action chain verified

Blocked scope test:

    python3 -m aapp.cli demo --scope examples/simple-tool-call/scope.blocked.json --out evidence/blocked-demo

Expected blocked result:

    BLOCKED: scope is not authorized
