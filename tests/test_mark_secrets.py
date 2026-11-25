import importlib.util
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "util" / "mark_secrets"
LOADER = SourceFileLoader("mark_secrets", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
mark_secrets = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(mark_secrets)


def mark(text: str) -> tuple[str, list[str]]:
    report: list[str] = []
    return mark_secrets.mark(text, report), report


class MarkSecretsTests(unittest.TestCase):
    def test_env_secrets_by_name_and_value(self) -> None:
        marked, report = mark(
            "DEBUG=0\n"
            'SECRET_KEY="x9Fk2LmQ8vPz4RtY7wNb3Hs"\n'
            "POSTGRES_HOST=/var/run/postgresql\n"
            "HOOK=https://discord.com/api/webhooks/1/abc\n"
            "DATABASE_URL=postgres://u:hunter2@db/x\n"
            "ID=QzzvIufaZhypvhMqUPHGO2CX9TQHGk\n"
        )
        self.assertEqual(
            marked,
            "DEBUG=0\n"
            'SECRET_KEY="!encrypt(x9Fk2LmQ8vPz4RtY7wNb3Hs)"\n'
            "POSTGRES_HOST=/var/run/postgresql\n"
            "HOOK=!encrypt(https://discord.com/api/webhooks/1/abc)\n"
            "DATABASE_URL=!encrypt(postgres://u:hunter2@db/x)\n"
            "ID=!encrypt(QzzvIufaZhypvhMqUPHGO2CX9TQHGk)\n",
        )
        self.assertIn("DEBUG: plain", report)
        self.assertFalse(any("hunter2" in line for line in report))

    def test_empty_and_harmless_values_stay_plain(self) -> None:
        marked, _ = mark("EMAIL_HOST_PASSWORD=\nAPI_KEY_FILE=/etc/key\n")
        self.assertEqual(
            marked, "EMAIL_HOST_PASSWORD=\nAPI_KEY_FILE=/etc/key\n"
        )

    def test_password_hashes(self) -> None:
        marked, _ = mark("klona:{PLAIN}x\nsuper:$apr1$ab$cd\n")
        self.assertEqual(
            marked, "klona:!encrypt({PLAIN}x)\nsuper:!encrypt($apr1$ab$cd)\n"
        )
        marked, _ = mark("users:\n  dash: pbkdf2:sha256:600000$a$b\n")
        self.assertIn("dash: !encrypt(pbkdf2:sha256:600000$a$b)", marked)

    def test_whole_file_secrets(self) -> None:
        key = "-----BEGIN KEY-----\nabc\n-----END KEY-----\n"
        self.assertEqual(mark(key)[0], f"!encrypt({key[:-1]})\n")
        self.assertEqual(mark("t0k3nvalue\n")[0], "!encrypt(t0k3nvalue)\n")

    def test_brackets_in_a_secret_pick_a_balanced_group(self) -> None:
        marked, _ = mark("password=a(b\n")
        self.assertEqual(marked, "password=!encrypt[a(b]\n")
