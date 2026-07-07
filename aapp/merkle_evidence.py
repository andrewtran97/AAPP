from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "aapp.merkle_evidence.v1"

VERIFIED = "VERIFIED"
FAILED = "FAILED"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
]


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def hex_bytes(digest: str) -> bytes:
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError("digest_must_be_sha256")
    return bytes.fromhex(digest.split(":", 1)[1])


def record_hash(record: dict[str, Any]) -> str:
    clean = dict(record)
    clean.pop("record_hash", None)
    return sha256_hex(b"AAPP_RECORD_V1\x00" + canonical_json(clean))


def leaf_hash(record_digest: str) -> str:
    return sha256_hex(b"\x00" + record_digest.encode("utf-8"))


def node_hash(left_hash: str, right_hash: str) -> str:
    return sha256_hex(b"\x01" + hex_bytes(left_hash) + hex_bytes(right_hash))


def largest_power_of_two_less_than(n: int) -> int:
    if n <= 1:
        raise ValueError("n_must_be_greater_than_1")
    return 1 << ((n - 1).bit_length() - 1)


def merkle_root(record_hashes: list[str]) -> str:
    n = len(record_hashes)
    if n == 0:
        return sha256_hex(b"")
    if n == 1:
        return leaf_hash(record_hashes[0])
    k = largest_power_of_two_less_than(n)
    return node_hash(merkle_root(record_hashes[:k]), merkle_root(record_hashes[k:]))


def inclusion_path(record_hashes: list[str], index: int) -> list[dict[str, str]]:
    n = len(record_hashes)
    if index < 0 or index >= n:
        raise ValueError("leaf_index_out_of_range")
    if n == 1:
        return []
    k = largest_power_of_two_less_than(n)
    if index < k:
        path = inclusion_path(record_hashes[:k], index)
        path.append({"side": "right", "hash": merkle_root(record_hashes[k:])})
        return path
    path = inclusion_path(record_hashes[k:], index - k)
    path.append({"side": "left", "hash": merkle_root(record_hashes[:k])})
    return path


def verify_inclusion_proof(record_digest: str, root_hash: str, path: list[dict[str, str]]) -> bool:
    current = leaf_hash(record_digest)
    try:
        for step in path:
            side = step["side"]
            sibling = step["hash"]
            if side == "right":
                current = node_hash(current, sibling)
            elif side == "left":
                current = node_hash(sibling, current)
            else:
                return False
    except Exception:
        return False
    return current == root_hash


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError("jsonl_row_not_object")
            rows.append(obj)
    return rows


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    with Path(path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def unsafe_findings(root: Path) -> list[dict[str, Any]]:
    findings = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if PRIVATE_KEY_RE.search(text):
            findings.append({"type": "private_key", "file_path": rel, "reason": "private key marker detected"})

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"type": "secret_pattern", "file_path": rel, "reason": "secret-like token detected"})
                break
    return findings


def consistency_proof(record_hashes: list[str], old_size: int) -> dict[str, Any]:
    if old_size <= 0 or old_size >= len(record_hashes):
        raise ValueError("old_size_must_be_between_1_and_new_size_minus_1")

    old_hashes = record_hashes[:old_size]
    return {
        "schema_version": "aapp.merkle_consistency_proof.v1",
        "old_tree_size": old_size,
        "new_tree_size": len(record_hashes),
        "old_root_hash": merkle_root(old_hashes),
        "new_root_hash": merkle_root(record_hashes),
        "record_hashes_for_prefix": old_hashes,
        "record_hashes_for_new_tree": record_hashes,
        "proof_model": "prefix-commitment-mvp",
    }


def verify_consistency_proof(proof: dict[str, Any]) -> bool:
    try:
        if proof.get("schema_version") != "aapp.merkle_consistency_proof.v1":
            return False
        old_size = int(proof["old_tree_size"])
        new_size = int(proof["new_tree_size"])
        prefix = proof["record_hashes_for_prefix"]
        new_hashes = proof["record_hashes_for_new_tree"]
        if old_size <= 0 or old_size >= new_size:
            return False
        if len(prefix) != old_size or len(new_hashes) != new_size:
            return False
        if new_hashes[:old_size] != prefix:
            return False
        return merkle_root(prefix) == proof["old_root_hash"] and merkle_root(new_hashes) == proof["new_root_hash"]
    except Exception:
        return False


def build_epoch(records_path: str | Path, out: str | Path, epoch_id: str = "epoch-000001") -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "inclusion").mkdir(parents=True, exist_ok=True)
    (out / "consistency").mkdir(parents=True, exist_ok=True)

    records = load_jsonl(records_path)
    if not records:
        raise ValueError("records_empty")

    enriched_records = []
    for idx, record in enumerate(records):
        rec = dict(record)
        rec.setdefault("record_id", f"record-{idx+1:06d}")
        rec.setdefault("seq", idx + 1)
        rec["record_hash"] = record_hash(rec)
        enriched_records.append(rec)

    record_hashes = [r["record_hash"] for r in enriched_records]
    root = merkle_root(record_hashes)

    leaves = []
    for idx, rec in enumerate(enriched_records):
        leaves.append({
            "leaf_index": idx,
            "record_id": rec["record_id"],
            "record_hash": rec["record_hash"],
            "leaf_hash": leaf_hash(rec["record_hash"]),
        })

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "epoch_id": epoch_id,
        "hash_alg": "SHA-256",
        "canonicalization": "python-json-sort-keys-separators-v1",
        "tree_size": len(record_hashes),
        "root_hash": root,
        "records_digest": sha256_hex(canonical_json(record_hashes)),
        "signed_tree_head_ref": "signed_tree_head.json",
        "records_ref": "records.jsonl",
        "leaves_ref": "leaves.jsonl",
    }

    sth_payload = {
        "schema_version": "aapp.signed_tree_head.v1",
        "epoch_id": epoch_id,
        "tree_size": len(record_hashes),
        "root_hash": root,
    }
    signed_tree_head = {
        **sth_payload,
        "signature_alg": "DEV-SHA256-PAYLOAD-DIGEST",
        "payload_digest": sha256_hex(canonical_json(sth_payload)),
        "signature": sha256_hex(b"AAPP_DEV_STH_SIGNATURE_V1\x00" + canonical_json(sth_payload)),
    }

    write_json(out / "manifest.json", manifest)
    write_json(out / "signed_tree_head.json", signed_tree_head)
    write_jsonl(out / "records.jsonl", enriched_records)
    write_jsonl(out / "leaves.jsonl", leaves)

    for leaf in leaves:
        proof = {
            "schema_version": "aapp.merkle_inclusion_proof.v1",
            "epoch_id": epoch_id,
            "record_id": leaf["record_id"],
            "leaf_index": leaf["leaf_index"],
            "tree_size": len(record_hashes),
            "record_hash": leaf["record_hash"],
            "leaf_hash": leaf["leaf_hash"],
            "root_hash": root,
            "path": inclusion_path(record_hashes, leaf["leaf_index"]),
        }
        write_json(out / "inclusion" / f"proof-{leaf['record_id']}.json", proof)

    if len(record_hashes) > 1:
        proof = consistency_proof(record_hashes, len(record_hashes) - 1)
        write_json(out / "consistency" / f"proof-from-{len(record_hashes)-1:06d}-to-{len(record_hashes):06d}.json", proof)

    report = [
        "# Merkle Evidence Transparency Receipt",
        "",
        f"- Epoch: `{epoch_id}`",
        f"- Tree size: `{len(record_hashes)}`",
        f"- Root hash: `{root}`",
        f"- Inclusion proofs: `{len(leaves)}`",
        f"- Consistency proof: `{'present' if len(record_hashes) > 1 else 'not_required'}`",
        "",
    ]
    (out / "merkle.report.md").write_text("\n".join(report), encoding="utf-8")

    return {
        "schema_version": SCHEMA_VERSION,
        "epoch_id": epoch_id,
        "tree_size": len(record_hashes),
        "root_hash": root,
    }


def verify_epoch(epoch_dir: str | Path, out: str | Path | None = None) -> dict[str, Any]:
    epoch = Path(epoch_dir)
    base = {
        "schema_version": "aapp.merkle_verdict.v1",
        "epoch_dir": str(epoch.resolve()),
        "verdict": None,
        "reason": None,
        "checks": [],
        "unsafe_findings": [],
    }

    if not epoch.exists() or not epoch.is_dir():
        return {**base, "verdict": MALFORMED, "reason": "epoch_dir_missing"}

    unsafe = unsafe_findings(epoch)
    if unsafe:
        verdict = {**base, "verdict": UNSAFE, "reason": "unsafe_content_detected", "unsafe_findings": unsafe}
    else:
        try:
            manifest = json.loads((epoch / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("schema_version") != SCHEMA_VERSION:
                verdict = {**base, "verdict": UNSUPPORTED, "reason": "unsupported_manifest_schema"}
            else:
                records = load_jsonl(epoch / "records.jsonl")
                recomputed_hashes = []
                for rec in records:
                    stored = rec.get("record_hash")
                    recomputed = record_hash(rec)
                    if stored != recomputed:
                        raise ValueError(f"record_hash_mismatch:{rec.get('record_id')}")
                    recomputed_hashes.append(recomputed)

                root = merkle_root(recomputed_hashes)
                if root != manifest.get("root_hash"):
                    raise ValueError("root_hash_mismatch")

                sth = json.loads((epoch / "signed_tree_head.json").read_text(encoding="utf-8"))
                payload = {
                    "schema_version": "aapp.signed_tree_head.v1",
                    "epoch_id": sth["epoch_id"],
                    "tree_size": sth["tree_size"],
                    "root_hash": sth["root_hash"],
                }
                if sth.get("payload_digest") != sha256_hex(canonical_json(payload)):
                    raise ValueError("signed_tree_head_payload_digest_mismatch")
                if sth.get("root_hash") != root:
                    raise ValueError("signed_tree_head_root_mismatch")

                checks = [{"type": "root", "ok": True, "root_hash": root}]

                for proof_path in sorted((epoch / "inclusion").glob("proof-*.json")):
                    proof = json.loads(proof_path.read_text(encoding="utf-8"))
                    ok = verify_inclusion_proof(proof["record_hash"], proof["root_hash"], proof["path"])
                    checks.append({"type": "inclusion", "file_path": proof_path.name, "ok": ok})
                    if not ok:
                        raise ValueError(f"inclusion_proof_invalid:{proof_path.name}")

                consistency_dir = epoch / "consistency"
                for proof_path in sorted(consistency_dir.glob("proof-*.json")):
                    proof = json.loads(proof_path.read_text(encoding="utf-8"))
                    ok = verify_consistency_proof(proof)
                    checks.append({"type": "consistency", "file_path": proof_path.name, "ok": ok})
                    if not ok:
                        raise ValueError(f"consistency_proof_invalid:{proof_path.name}")

                verdict = {**base, "verdict": VERIFIED, "reason": "all_checks_passed", "checks": checks}
        except FileNotFoundError as exc:
            verdict = {**base, "verdict": MALFORMED, "reason": f"missing_file:{Path(str(exc)).name}"}
        except json.JSONDecodeError:
            verdict = {**base, "verdict": MALFORMED, "reason": "json_decode_error"}
        except Exception as exc:
            verdict = {**base, "verdict": FAILED, "reason": str(exc)}

    if out is not None:
        out_path = Path(out)
        out_path.mkdir(parents=True, exist_ok=True)
        write_json(out_path / "merkle.verdict.json", verdict)
        lines = [
            "# Merkle Evidence Verification",
            "",
            f"- Verdict: `{verdict['verdict']}`",
            f"- Reason: `{verdict['reason']}`",
            f"- Checks: `{len(verdict.get('checks', []))}`",
            f"- Unsafe findings: `{len(verdict.get('unsafe_findings', []))}`",
            "",
        ]
        (out_path / "merkle.report.md").write_text("\n".join(lines), encoding="utf-8")

    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merkle evidence transparency receipt.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build")
    build.add_argument("--records", required=True)
    build.add_argument("--out", required=True)
    build.add_argument("--epoch-id", default="epoch-000001")

    verify = sub.add_parser("verify")
    verify.add_argument("--epoch-dir", required=True)
    verify.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "build":
        result = build_epoch(args.records, args.out, epoch_id=args.epoch_id)
        print(f"AAPP merkle build complete: tree_size={result['tree_size']} root={result['root_hash']} out={Path(args.out).resolve()}")
        return 0

    verdict = verify_epoch(args.epoch_dir, out=args.out)
    print(f"AAPP merkle verify complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
    return 0 if verdict["verdict"] == VERIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
