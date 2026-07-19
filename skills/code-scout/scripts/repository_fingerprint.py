#!/usr/bin/env python3
"""Print a bounded, content-sensitive fingerprint for a Git worktree."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import stat
import subprocess
import sys
import tempfile
import time


CHUNK_SIZE = 1024 * 1024
MAX_FINGERPRINT_BYTES = 256 * 1024 * 1024
MAX_GIT_METADATA_BYTES = 32 * 1024 * 1024
COMMAND_TIMEOUT_SECONDS = 60.0
HEAD_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


@dataclass
class ByteBudget:
    remaining: int

    def consume(self, size: int) -> None:
        if size > self.remaining:
            raise RuntimeError(
                "fingerprint input exceeds "
                f"{MAX_FINGERPRINT_BYTES} byte safety limit"
            )
        self.remaining -= size


def git_bytes(root: Path, *args: str, allow_failure: bool = False) -> bytes | None:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"git {' '.join(args)} timed out") from error
    if len(result.stdout) > MAX_GIT_METADATA_BYTES:
        raise RuntimeError(
            f"git {' '.join(args)} output exceeds metadata safety limit"
        )
    if result.returncode != 0:
        if allow_failure:
            return None
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout


def update_record(digest: "hashlib._Hash", label: bytes, payload: bytes) -> None:
    digest.update(len(label).to_bytes(8, "big"))
    digest.update(label)
    digest.update(len(payload).to_bytes(8, "big"))
    digest.update(payload)


def hash_git_stream(
    digest: "hashlib._Hash",
    budget: ByteBudget,
    root: Path,
    label: bytes,
    *args: str,
) -> None:
    payload_digest = hashlib.sha256()
    payload_size = 0
    started_at = time.monotonic()

    with tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(
            ["git", "-C", os.fspath(root), *args],
            stdout=subprocess.PIPE,
            stderr=stderr,
        )
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        try:
            while selector.get_map():
                remaining_time = COMMAND_TIMEOUT_SECONDS - (
                    time.monotonic() - started_at
                )
                if remaining_time <= 0:
                    process.kill()
                    process.wait()
                    raise RuntimeError(f"git {' '.join(args)} timed out")
                if not selector.select(remaining_time):
                    process.kill()
                    process.wait()
                    raise RuntimeError(f"git {' '.join(args)} timed out")
                chunk = process.stdout.read(CHUNK_SIZE)
                if chunk:
                    budget.consume(len(chunk))
                    payload_size += len(chunk)
                    payload_digest.update(chunk)
                else:
                    selector.unregister(process.stdout)
        except BaseException:
            if process.poll() is None:
                process.kill()
            process.wait()
            raise
        finally:
            selector.close()
            process.stdout.close()

        remaining_time = COMMAND_TIMEOUT_SECONDS - (
            time.monotonic() - started_at
        )
        try:
            returncode = process.wait(timeout=max(remaining_time, 0.001))
        except subprocess.TimeoutExpired as error:
            process.kill()
            process.wait()
            raise RuntimeError(f"git {' '.join(args)} timed out") from error
        if returncode != 0:
            stderr.seek(0)
            message = stderr.read(MAX_GIT_METADATA_BYTES).decode(
                "utf-8", errors="replace"
            ).strip()
            raise RuntimeError(message or f"git {' '.join(args)} failed")

    update_record(
        digest,
        label,
        payload_size.to_bytes(8, "big") + payload_digest.digest(),
    )


def hash_untracked_file(
    digest: "hashlib._Hash",
    budget: ByteBudget,
    repository_root: Path,
    encoded_path: bytes,
) -> None:
    relative_path = os.fsdecode(encoded_path)
    absolute_path = repository_root / relative_path
    update_record(digest, b"untracked-path", encoded_path)

    before = absolute_path.lstat()
    update_record(digest, b"untracked-mode", before.st_mode.to_bytes(8, "big"))
    if stat.S_ISLNK(before.st_mode):
        target = os.fsencode(os.readlink(absolute_path))
        budget.consume(len(target))
        update_record(digest, b"untracked-symlink", target)
        return
    if not stat.S_ISREG(before.st_mode):
        update_record(digest, b"untracked-special", b"")
        return

    file_digest = hashlib.sha256()
    size = 0
    with absolute_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            budget.consume(len(chunk))
            size += len(chunk)
            file_digest.update(chunk)

    after = absolute_path.lstat()
    stable_fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        raise RuntimeError(f"worktree changed while reading {relative_path}")
    update_record(
        digest,
        b"untracked-file",
        size.to_bytes(8, "big") + file_digest.digest(),
    )


def fingerprint(root_arg: str) -> dict[str, str]:
    requested_root = Path(root_arg).expanduser().resolve(strict=True)
    raw_repository_root = git_bytes(
        requested_root, "rev-parse", "--show-toplevel"
    )
    assert raw_repository_root is not None
    repository_root = Path(
        raw_repository_root.decode("utf-8").strip()
    ).resolve(strict=True)
    if requested_root != repository_root:
        raise RuntimeError(
            f"expected repository root {repository_root}, got {requested_root}"
        )

    raw_head = git_bytes(
        repository_root, "rev-parse", "--verify", "HEAD", allow_failure=True
    )
    head = "unborn" if raw_head is None else raw_head.decode("ascii").strip()
    if head != "unborn" and HEAD_PATTERN.fullmatch(head) is None:
        raise RuntimeError("repository HEAD is not a supported Git object ID")

    status_before = git_bytes(
        repository_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    untracked_before = git_bytes(
        repository_root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    )
    assert status_before is not None and untracked_before is not None

    digest = hashlib.sha256()
    budget = ByteBudget(remaining=MAX_FINGERPRINT_BYTES)
    update_record(digest, b"status", status_before)
    if head == "unborn":
        hash_git_stream(
            digest,
            budget,
            repository_root,
            b"index-diff",
            "diff",
            "--cached",
            "--no-ext-diff",
            "--no-textconv",
            "--binary",
            "--",
        )
        hash_git_stream(
            digest,
            budget,
            repository_root,
            b"worktree-diff",
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--binary",
            "--",
        )
    else:
        hash_git_stream(
            digest,
            budget,
            repository_root,
            b"tracked-diff",
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--binary",
            "--submodule=diff",
            "HEAD",
            "--",
        )

    untracked_paths = sorted(
        path for path in untracked_before.split(b"\0") if path
    )
    for encoded_path in untracked_paths:
        hash_untracked_file(
            digest, budget, repository_root, encoded_path
        )

    status_after = git_bytes(
        repository_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    untracked_after = git_bytes(
        repository_root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    )
    if status_after != status_before or untracked_after != untracked_before:
        raise RuntimeError("worktree changed while fingerprinting")

    return {"head": head, "worktree_sha256": digest.hexdigest()}


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "usage: repository_fingerprint.py <repository-root>",
            file=sys.stderr,
        )
        return 2
    try:
        result = fingerprint(sys.argv[1])
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"repository fingerprint failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
