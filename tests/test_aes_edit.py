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


class MarkedFileTests(unittest.TestCase):
    PLAIN = (
        "password = !encrypt(hunter2)\n"
        'const char *const token = "!encrypt[a(b)c]";\n'
        "nested = !encrypt(f(o(o)))\n"
        "key = !encrypt{\n-----BEGIN KEY-----\nabc\n-----END KEY-----\n}\n"
        "plain = stays readable\n"
    )

    def setUp(self) -> None:
        self.file = aes_edit.MarkedFile.create("pw")

    def test_round_trip_keeps_the_text(self) -> None:
        sealed = self.file.seal(self.PLAIN)
        opened, plain = aes_edit.MarkedFile.open(sealed, "pw")
        self.assertEqual(plain, self.PLAIN)
        self.assertEqual(opened.tokens, ("encrypt", "decrypt"))

    def test_only_the_groups_are_encrypted(self) -> None:
        sealed = self.file.seal(self.PLAIN).decode()
        for secret in ["hunter2", "a(b)c", "f(o(o))", "BEGIN KEY"]:
            self.assertNotIn(secret, sealed)
        self.assertIn("plain = stays readable\n", sealed)
        self.assertIn('const char *const token = "!decrypt[', sealed)
        self.assertTrue(aes_edit.is_marked_file(sealed.encode()))

    def test_reveal_drops_the_tokens(self) -> None:
        self.assertEqual(
            self.file.reveal("a = !encrypt(x(y))\nb = !encrypt[z]\n"),
            "a = x(y)\nb = z\n",
        )

    def test_unchanged_secrets_keep_their_ciphertext(self) -> None:
        first = self.file.seal(self.PLAIN).decode().splitlines()
        opened, plain = aes_edit.MarkedFile.open(
            "\n".join(first).encode() + b"\n", "pw"
        )
        second = (
            opened.seal(plain.replace("hunter2", "hunter3"))
            .decode()
            .splitlines()
        )
        changed = [i for i, (a, b) in enumerate(zip(first, second)) if a != b]
        self.assertEqual(changed, [0, 1])

    def test_wrong_password_and_tampering_are_refused(self) -> None:
        sealed = self.file.seal(self.PLAIN)
        with self.assertRaises(aes_edit.InvalidKey):
            aes_edit.MarkedFile.open(sealed, "wrong")
        tampered = sealed.replace(b"stays readable", b"was changed")
        with self.assertRaises(aes_edit.InvalidKey):
            aes_edit.MarkedFile.open(tampered, "pw")

    def test_custom_tokens(self) -> None:
        file = aes_edit.MarkedFile.create("pw", ("prince", "princess"))
        sealed = file.seal("crown = !prince<jewel>\n")
        self.assertIn(b"!princess-file(v2 tokens=prince,princess", sealed)
        self.assertIn(b"crown = !princess<", sealed)
        opened, plain = aes_edit.MarkedFile.open(sealed, "pw")
        self.assertEqual(plain, "crown = !prince<jewel>\n")

    def test_one_token_twice_is_refused(self) -> None:
        with self.assertRaises(aes_edit.MarkupError):
            aes_edit.MarkedFile.create("pw", ("same", "same"))

    def test_a_token_may_start_the_other(self) -> None:
        text = "a = !prince(x) b = !princess-ish\n"
        file = aes_edit.MarkedFile.create("pw", ("prince", "princess"))
        self.assertEqual(
            aes_edit.MarkedFile.open(file.seal(text), "pw")[1], text
        )

    def test_unbalanced_group_is_refused(self) -> None:
        with self.assertRaises(aes_edit.MarkupError):
            self.file.seal("x = !encrypt(open\n")

    def test_sealed_token_in_the_editor_is_refused(self) -> None:
        with self.assertRaises(aes_edit.MarkupError):
            self.file.seal("x = !decrypt(not ciphertext)\n")

    def test_old_files_are_told_apart(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            old = Path(scratch) / "old.aes"
            aes_edit.write_encrypted_file(old, "pw", "x = (1\n")
            self.assertFalse(aes_edit.is_marked_file(old.read_bytes()))
            content = aes_edit.read_encrypted_file(old, "pw")
            self.assertEqual(
                aes_edit.wrap("encrypt", content), "!encrypt[x = (1\n]"
            )
