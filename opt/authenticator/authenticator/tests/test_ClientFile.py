import tempfile
import unittest
from pathlib import Path
from typing import Any

from authenticator.data import ClientData, ClientFile


class CoreClientFileTests(unittest.TestCase):
    """Tests for the data module."""

    def test_save_load(self) -> None:
        """Test for Save(), Load().

        Ensure a simple Save() and Load() work as expected.

        """

        expected = []
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
        }
        expected.append(ClientData(**args))
        args = {
            "client_id": "You.Dont.Say",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
        }
        expected.append(ClientData(**args))
        args = {
            "client_id": "Well.I.Never",
            "shared_secret": "ABCDGNBVGY3TQOJQGEZDGNBVGY3TQCBA",
            "password_length": 8,
            "period": 15,
        }
        expected.append(ClientData(**args))

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "hotp.data"
            cut = ClientFile(filepath)
            cut.save(expected)
            actual = cut.load()
            self.assertEqual(expected, actual)
