from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


PROFILE = "openssl-ed25519-detached"
PRIVATE_NAME = "ed25519_private.pem"
PUBLIC_NAME = "ed25519_public.pem"
SIGNATURE_NAME = "manifest.ed25519.sig"
PROFILE_NAME = "signature.profile.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(args: list[str], cwd: Path | None = None) -> Tuple[str, str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")
    return result.stdout, result.stderr


def _sha384_file(path: Path) -> str:
    return hashlib.sha384(path.read_bytes()).hexdigest()


def _read_profile(bundle_dir: Path) -> Dict[str, Any]:
    path = bundle_dir / PROFILE_NAME
    if not path.is_file():
        raise FileNotFoundError(f"missing signature profile: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("signature profile must be a JSON object")
    return value


def generate_ed25519(out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)

    private_key = out_dir / PRIVATE_NAME
    public_key = out_dir / PUBLIC_NAME

    _run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)])
    _run(["openssl", "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)])

    try:
        private_key.chmod(0o600)
    except OSError:
        pass

    return {
        "private_key": str(private_key),
        "public_key": str(public_key),
    }


def sign_bundle(bundle_dir: Path, private_key: Path, public_key: Path) -> Dict[str, str]:
    bundle_dir = bundle_dir.resolve()
    manifest = bundle_dir / "manifest.json"

    if not manifest.is_file():
        raise FileNotFoundError(f"missing manifest: {manifest}")
    if not private_key.is_file():
        raise FileNotFoundError(f"missing private key: {private_key}")
    if not public_key.is_file():
        raise FileNotFoundError(f"missing public key: {public_key}")

    signature = bundle_dir / SIGNATURE_NAME
    public_key_in_bundle = bundle_dir / PUBLIC_NAME

    _run([
        "openssl", "pkeyutl",
        "-sign",
        "-rawin",
        "-inkey", str(private_key),
        "-in", str(manifest),
        "-out", str(signature),
    ])

    shutil.copy2(public_key, public_key_in_bundle)

    profile: Dict[str, Any] = {
        "schema_version": "aapp.production_signature.v1",
        "signature_profile": PROFILE,
        "created_at": _utc_now(),
        "signed_file": "manifest.json",
        "signed_file_sha384": _sha384_file(manifest),
        "signature_file": SIGNATURE_NAME,
        "public_key_file": PUBLIC_NAME,
    }

    (bundle_dir / PROFILE_NAME).write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return {
        "bundle_dir": str(bundle_dir),
        "signature_file": str(signature),
        "public_key_file": str(public_key_in_bundle),
        "profile_file": str(bundle_dir / PROFILE_NAME),
    }


def verify_bundle_signature(bundle_dir: Path, public_key: Path | None = None) -> Tuple[bool, str]:
    bundle_dir = bundle_dir.resolve()
    profile = _read_profile(bundle_dir)

    if profile.get("signature_profile") != PROFILE:
        return False, "unsupported signature profile"

    manifest = bundle_dir / str(profile.get("signed_file", ""))
    signature = bundle_dir / str(profile.get("signature_file", ""))

    if public_key is None:
        public_key = bundle_dir / str(profile.get("public_key_file", ""))

    if not manifest.is_file():
        return False, "missing signed manifest"
    if not signature.is_file():
        return False, "missing detached signature"
    if not public_key.is_file():
        return False, "missing public key"

    expected_digest = profile.get("signed_file_sha384")
    actual_digest = _sha384_file(manifest)
    if expected_digest != actual_digest:
        return False, "signed file digest mismatch"

    try:
        _run([
            "openssl", "pkeyutl",
            "-verify",
            "-rawin",
            "-pubin",
            "-inkey", str(public_key),
            "-sigfile", str(signature),
            "-in", str(manifest),
        ])
    except RuntimeError as exc:
        return False, f"signature verification failed: {exc}"

    return True, "signature verified"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Black Box production signing interface")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("gen-ed25519", help="Generate local Ed25519 signing keypair")
    gen.add_argument("--out", required=True)

    sign = sub.add_parser("sign-bundle", help="Create detached Ed25519 signature for bundle manifest")
    sign.add_argument("--bundle-dir", required=True)
    sign.add_argument("--private-key", required=True)
    sign.add_argument("--public-key", required=True)

    verify = sub.add_parser("verify-bundle", help="Verify detached Ed25519 signature for bundle manifest")
    verify.add_argument("--bundle-dir", required=True)
    verify.add_argument("--public-key")

    ns = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if ns.cmd == "gen-ed25519":
            print(json.dumps(generate_ed25519(Path(ns.out)), sort_keys=True))
            return 0

        if ns.cmd == "sign-bundle":
            print(json.dumps(sign_bundle(Path(ns.bundle_dir), Path(ns.private_key), Path(ns.public_key)), sort_keys=True))
            return 0

        if ns.cmd == "verify-bundle":
            ok, message = verify_bundle_signature(
                Path(ns.bundle_dir),
                Path(ns.public_key) if ns.public_key else None,
            )
            print(("PASS: " if ok else "FAIL: ") + message)
            return 0 if ok else 1

        raise AssertionError(ns.cmd)

    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
