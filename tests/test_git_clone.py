import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from libdotfiles.util import git_clone


class GitCloneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.target = Path(self.scratch.name) / "checkout"
        self.repo = "https://example.invalid/repo"

    def test_existing_non_repository_is_rejected_before_running_git(
        self,
    ) -> None:
        self.target.mkdir()
        with patch("libdotfiles.util.run") as run:
            with self.assertRaisesRegex(RuntimeError, "not a git repository"):
                git_clone(self.repo, self.target)
        run.assert_not_called()

    def test_wrong_remote_is_rejected(self) -> None:
        (self.target / ".git").mkdir(parents=True)
        with patch(
            "libdotfiles.util.run",
            return_value=subprocess.CompletedProcess([], 0, "wrong\n"),
        ):
            with self.assertRaisesRegex(RuntimeError, "expected"):
                git_clone(self.repo, self.target)

    def test_matching_remote_accepts_dot_git_suffix(self) -> None:
        (self.target / ".git").mkdir(parents=True)
        with patch(
            "libdotfiles.util.run",
            return_value=subprocess.CompletedProcess(
                [], 0, self.repo + ".git\n"
            ),
        ) as run:
            git_clone(self.repo, self.target)
        run.assert_called_once()

    def test_missing_checkout_is_cloned(self) -> None:
        with patch("libdotfiles.util.run") as run:
            git_clone(self.repo, self.target)
        run.assert_called_once_with(
            ["git", "clone", self.repo, self.target], check=True
        )
