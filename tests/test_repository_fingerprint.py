from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "code-scout"
    / "scripts"
    / "repository_fingerprint.py"
)
SPEC = importlib.util.spec_from_file_location("repository_fingerprint", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
repository_fingerprint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = repository_fingerprint
SPEC.loader.exec_module(repository_fingerprint)


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", os.fspath(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class RepositoryFingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Code Scout Test")
        git(self.root, "config", "user.email", "code-scout@example.invalid")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def fingerprint(self) -> dict[str, str]:
        return repository_fingerprint.fingerprint(os.fspath(self.root))

    def commit_file(self, name: str = "tracked.txt", content: str = "base\n") -> None:
        (self.root / name).write_text(content, encoding="utf-8")
        git(self.root, "add", name)
        git(self.root, "commit", "-qm", "fixture")

    def test_unborn_repository_is_supported_and_content_sensitive(self) -> None:
        initial = self.fingerprint()
        self.assertEqual(initial["head"], "unborn")
        self.assertEqual(initial, self.fingerprint())

        (self.root / "new.txt").write_text("one\n", encoding="utf-8")
        first = self.fingerprint()
        (self.root / "new.txt").write_text("two\n", encoding="utf-8")
        second = self.fingerprint()

        self.assertEqual(first["head"], "unborn")
        self.assertNotEqual(initial["worktree_sha256"], first["worktree_sha256"])
        self.assertNotEqual(first["worktree_sha256"], second["worktree_sha256"])

    def test_tracked_changes_are_stable_and_reversible(self) -> None:
        self.commit_file()
        clean = self.fingerprint()
        self.assertRegex(clean["head"], r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
        self.assertEqual(clean, self.fingerprint())

        (self.root / "tracked.txt").write_text("changed\n", encoding="utf-8")
        changed = self.fingerprint()
        self.assertNotEqual(clean["worktree_sha256"], changed["worktree_sha256"])

        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        self.assertEqual(clean, self.fingerprint())

    def test_untracked_mode_and_content_affect_fingerprint(self) -> None:
        self.commit_file()
        path = self.root / "script.sh"
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o644)
        regular = self.fingerprint()

        path.chmod(0o755)
        executable = self.fingerprint()
        self.assertNotEqual(
            regular["worktree_sha256"], executable["worktree_sha256"]
        )

        path.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        changed = self.fingerprint()
        self.assertNotEqual(
            executable["worktree_sha256"], changed["worktree_sha256"]
        )

    def test_total_input_limit_is_enforced(self) -> None:
        self.commit_file()
        (self.root / "large.bin").write_bytes(b"x" * 32)
        original_limit = repository_fingerprint.MAX_FINGERPRINT_BYTES
        try:
            repository_fingerprint.MAX_FINGERPRINT_BYTES = 16
            with self.assertRaisesRegex(RuntimeError, "safety limit"):
                self.fingerprint()
        finally:
            repository_fingerprint.MAX_FINGERPRINT_BYTES = original_limit

    def test_requires_the_exact_repository_root(self) -> None:
        child = self.root / "child"
        child.mkdir()
        with self.assertRaisesRegex(RuntimeError, "expected repository root"):
            repository_fingerprint.fingerprint(os.fspath(child))


if __name__ == "__main__":
    unittest.main()
