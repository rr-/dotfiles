import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "util" / "aes-edit"
LOADER = SourceFileLoader("aes_edit", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
aes_edit = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(aes_edit)


class EncryptedSaveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.target = self.root / "notes.aes"
        aes_edit.write_encrypted_file(self.target, "password", "original")

    def test_successful_save_round_trips_and_is_private(self) -> None:
        aes_edit.write_encrypted_file(self.target, "password", "new text")
        self.assertEqual(
            aes_edit.read_encrypted_file(self.target, "password"), "new text"
        )
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(list(self.root.iterdir()), [self.target])

    def test_failed_save_preserves_previous_ciphertext(self) -> None:
        original = self.target.read_bytes()
        with patch.object(
            aes_edit.os, "fsync", side_effect=OSError("disk full")
        ):
            with self.assertRaises(OSError):
                aes_edit.write_encrypted_file(self.target, "password", "new")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(list(self.root.iterdir()), [self.target])

    def test_failed_replace_preserves_previous_ciphertext(self) -> None:
        original = self.target.read_bytes()
        with patch.object(Path, "replace", side_effect=OSError("read only")):
            with self.assertRaises(OSError):
                aes_edit.write_encrypted_file(self.target, "password", "new")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(list(self.root.iterdir()), [self.target])

    def test_save_through_symlink_preserves_the_link(self) -> None:
        link = self.root / "link"
        link.symlink_to(self.target)
        aes_edit.write_encrypted_file(link, "password", "updated")
        self.assertTrue(link.is_symlink())
        self.assertEqual(
            aes_edit.read_encrypted_file(self.target, "password"), "updated"
        )
