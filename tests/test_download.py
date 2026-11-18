import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from libdotfiles.util import download_file


class DownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.target = self.root / "artifact"

    def test_success_and_existing_file_is_skipped(self) -> None:
        with patch(
            "urllib.request.urlopen", return_value=io.BytesIO(b"complete")
        ) as network:
            download_file("https://example.invalid/file", self.target)
            download_file("https://example.invalid/file", self.target)
        self.assertEqual(self.target.read_bytes(), b"complete")
        network.assert_called_once()
        self.assertEqual(list(self.root.iterdir()), [self.target])

    def test_failed_download_leaves_no_file_and_can_be_retried(self) -> None:
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.side_effect = [b"partial", OSError("disconnected")]
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(OSError):
                download_file("https://example.invalid/file", self.target)
        self.assertEqual(list(self.root.iterdir()), [])
        with patch(
            "urllib.request.urlopen", return_value=io.BytesIO(b"complete")
        ):
            download_file("https://example.invalid/file", self.target)
        self.assertEqual(self.target.read_bytes(), b"complete")

    def test_failed_overwrite_preserves_original(self) -> None:
        self.target.write_bytes(b"original")
        with (
            patch("urllib.request.urlopen", return_value=io.BytesIO(b"new")),
            patch(
                "libdotfiles.util.os.fsync", side_effect=OSError("disk full")
            ),
        ):
            with self.assertRaises(OSError):
                download_file(
                    "https://example.invalid/file", self.target, overwrite=True
                )
        self.assertEqual(self.target.read_bytes(), b"original")
        self.assertEqual(list(self.root.iterdir()), [self.target])
