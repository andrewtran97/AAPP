import json
import shutil
from pathlib import Path

from aapp.merkle_evidence import (
    FAILED,
    UNSAFE,
    VERIFIED,
    build_epoch,
    consistency_proof,
    load_jsonl,
    record_hash,
    verify_consistency_proof,
    verify_epoch,
    verify_inclusion_proof,
)


FIXTURE = Path(__file__).parent / "fixtures" / "merkle_evidence" / "records.jsonl"


def test_build_and_verify_epoch(tmp_path):
    epoch = tmp_path / "epoch-000001"
    build_epoch(FIXTURE, epoch, epoch_id="epoch-000001")

    verdict = verify_epoch(epoch, out=tmp_path / "verify")

    assert verdict["verdict"] == VERIFIED
    assert (epoch / "manifest.json").exists()
    assert (epoch / "signed_tree_head.json").exists()
    assert (epoch / "leaves.jsonl").exists()
    assert (epoch / "records.jsonl").exists()
    assert (epoch / "inclusion").exists()
    assert (epoch / "consistency").exists()
    assert (tmp_path / "verify" / "merkle.verdict.json").exists()
    assert (tmp_path / "verify" / "merkle.report.md").exists()


def test_single_leaf_tree_verifies(tmp_path):
    one = tmp_path / "one.jsonl"
    first = FIXTURE.read_text().splitlines()[0]
    one.write_text(first + "\n", encoding="utf-8")

    epoch = tmp_path / "single"
    build_epoch(one, epoch, epoch_id="single")

    verdict = verify_epoch(epoch)
    assert verdict["verdict"] == VERIFIED

    proofs = list((epoch / "inclusion").glob("proof-*.json"))
    assert len(proofs) == 1
    proof = json.loads(proofs[0].read_text())
    assert proof["path"] == []


def test_odd_leaf_count_and_non_power_of_two_verifies(tmp_path):
    epoch = tmp_path / "odd"
    build_epoch(FIXTURE, epoch, epoch_id="odd")

    manifest = json.loads((epoch / "manifest.json").read_text())
    assert manifest["tree_size"] == 5

    verdict = verify_epoch(epoch)
    assert verdict["verdict"] == VERIFIED


def test_tampered_record_fails(tmp_path):
    epoch = tmp_path / "tampered"
    build_epoch(FIXTURE, epoch, epoch_id="tampered")

    lines = (epoch / "records.jsonl").read_text().splitlines()
    rec = json.loads(lines[1])
    rec["policy_decision"] = "ALLOW"
    lines[1] = json.dumps(rec, sort_keys=True)
    (epoch / "records.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    verdict = verify_epoch(epoch)
    assert verdict["verdict"] == FAILED
    assert "record_hash_mismatch" in verdict["reason"]


def test_swapped_sibling_direction_fails(tmp_path):
    epoch = tmp_path / "epoch"
    build_epoch(FIXTURE, epoch, epoch_id="epoch")

    proof_path = sorted((epoch / "inclusion").glob("proof-*.json"))[2]
    proof = json.loads(proof_path.read_text())

    assert verify_inclusion_proof(proof["record_hash"], proof["root_hash"], proof["path"]) is True

    if proof["path"]:
        proof["path"][0]["side"] = "left" if proof["path"][0]["side"] == "right" else "right"
        assert verify_inclusion_proof(proof["record_hash"], proof["root_hash"], proof["path"]) is False


def test_consistency_proof_verifies_and_invalid_fails():
    records = load_jsonl(FIXTURE)
    hashes = [record_hash(r) for r in records]

    proof = consistency_proof(hashes, old_size=4)
    assert verify_consistency_proof(proof) is True

    proof["old_root_hash"] = "sha256:" + ("0" * 64)
    assert verify_consistency_proof(proof) is False


def test_private_key_package_unsafe(tmp_path):
    epoch = tmp_path / "unsafe"
    build_epoch(FIXTURE, epoch, epoch_id="unsafe")

    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    (epoch / "unsafe.pem").write_text(marker + "\nnot-real\n", encoding="utf-8")

    verdict = verify_epoch(epoch)
    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_machine_readable_verdict(tmp_path):
    epoch = tmp_path / "epoch"
    out = tmp_path / "verify"
    build_epoch(FIXTURE, epoch, epoch_id="epoch")
    verify_epoch(epoch, out=out)

    verdict = json.loads((out / "merkle.verdict.json").read_text())
    assert verdict["schema_version"] == "aapp.merkle_verdict.v1"
    assert verdict["verdict"] == VERIFIED


def test_consistency_file_invalid_fails_epoch_verify(tmp_path):
    epoch = tmp_path / "epoch"
    build_epoch(FIXTURE, epoch, epoch_id="epoch")

    proof_path = next((epoch / "consistency").glob("proof-*.json"))
    proof = json.loads(proof_path.read_text())
    proof["new_root_hash"] = "sha256:" + ("f" * 64)
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    verdict = verify_epoch(epoch)
    assert verdict["verdict"] == FAILED
    assert "consistency_proof_invalid" in verdict["reason"]
