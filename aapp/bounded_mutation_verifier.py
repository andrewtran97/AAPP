"""Independent filesystem verifier for the B44B bounded mutation workflow."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple


VERIFIED = "VERIFIED"
FAILED = "FAILED"


class VerificationError(ValueError):
    """Raised when the verifier cannot safely inspect the declared target."""


def digest_bytes(data: bytes) -> str:
    return "sha384:" + hashlib.sha384(data).hexdigest()


def _canonical_relative_parts(value: str) -> Tuple[str, ...]:
    if not isinstance(value, str) or not value:
        raise VerificationError("target relative path is required")
    if "\\" in value:
        raise VerificationError("backslash path separators are unsupported")

    path = PurePosixPath(value)
    if path.is_absolute():
        raise VerificationError("absolute target paths are forbidden")
    if path.as_posix() != value:
        raise VerificationError("target relative path must be canonical")

    parts = path.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise VerificationError("path traversal or empty components are forbidden")
    return parts


def _open_target(workspace_root: str, target_relative_path: str) -> int:
    root = Path(workspace_root)
    if not root.is_absolute():
        raise VerificationError("workspace root must be absolute")
    if root.is_symlink():
        raise VerificationError("workspace root symlink is forbidden")

    resolved_root = root.resolve(strict=True)
    parts = _canonical_relative_parts(target_relative_path)

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    directory = getattr(os, "O_DIRECTORY", 0)

    root_fd = os.open(str(resolved_root), os.O_RDONLY | directory | nofollow | cloexec)
    current_fd = root_fd
    try:
        for part in parts[:-1]:
            parent_metadata = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
            if stat.S_ISLNK(parent_metadata.st_mode):
                raise VerificationError("parent symlink is forbidden")
            next_fd = os.open(
                part,
                os.O_RDONLY | directory | nofollow | cloexec,
                dir_fd=current_fd,
            )
            if current_fd != root_fd:
                os.close(current_fd)
            current_fd = next_fd

        target_metadata = os.stat(
            parts[-1],
            dir_fd=current_fd,
            follow_symlinks=False,
        )
        if stat.S_ISLNK(target_metadata.st_mode):
            raise VerificationError("target symlink is forbidden")
        target_fd = os.open(
            parts[-1],
            os.O_RDONLY | nofollow | cloexec,
            dir_fd=current_fd,
        )
        return target_fd
    except OSError as exc:
        raise VerificationError("target cannot be opened safely") from exc
    finally:
        if current_fd != root_fd:
            os.close(current_fd)
        os.close(root_fd)


def _read_all(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: List[bytes] = []
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def verify_mutation_state(
    *,
    workspace_root: str,
    target_relative_path: str,
    expected_post_state_digest: str,
    expected_device: int,
    expected_inode: int,
) -> Dict[str, Any]:
    """Inspect actual filesystem state without trusting workflow-reported bytes."""

    try:
        fd = _open_target(workspace_root, target_relative_path)
    except (OSError, VerificationError):
        return {
            "verdict": FAILED,
            "reason_codes": ["TARGET_UNREADABLE"],
            "actual_post_state_digest": None,
        }

    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            return {
                "verdict": FAILED,
                "reason_codes": ["TARGET_NOT_REGULAR_FILE"],
                "actual_post_state_digest": None,
            }
        if metadata.st_nlink != 1:
            return {
                "verdict": FAILED,
                "reason_codes": ["TARGET_HARD_LINKED"],
                "actual_post_state_digest": None,
            }
        if metadata.st_dev != expected_device or metadata.st_ino != expected_inode:
            return {
                "verdict": FAILED,
                "reason_codes": ["TARGET_IDENTITY_CHANGED"],
                "actual_post_state_digest": None,
            }

        actual_digest = digest_bytes(_read_all(fd))
        if actual_digest != expected_post_state_digest:
            return {
                "verdict": FAILED,
                "reason_codes": ["POST_STATE_DIGEST_MISMATCH"],
                "actual_post_state_digest": actual_digest,
            }

        return {
            "verdict": VERIFIED,
            "reason_codes": ["ACTUAL_FILESYSTEM_STATE_VERIFIED"],
            "actual_post_state_digest": actual_digest,
        }
    except OSError:
        return {
            "verdict": FAILED,
            "reason_codes": ["TARGET_READ_FAILED"],
            "actual_post_state_digest": None,
        }
    finally:
        os.close(fd)
