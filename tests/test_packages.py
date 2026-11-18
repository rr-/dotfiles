import subprocess
import unittest
from unittest.mock import Mock, patch

from libdotfiles.packages import (
    AptPackageInstaller,
    PipPackageInstaller,
    install,
    try_install,
)


class PackageTests(unittest.TestCase):
    def test_failed_required_install_raises(self) -> None:
        installer = Mock(name="installer")
        installer.name = "test"
        installer.has_installed.return_value = False
        installer.is_available.return_value = True
        installer.install.return_value = False
        with patch("libdotfiles.packages.INSTALLERS", [installer]):
            with self.assertRaisesRegex(RuntimeError, "Failed to install"):
                install("example")

    def test_optional_install_returns_false_on_failure(self) -> None:
        with patch(
            "libdotfiles.packages.install", side_effect=RuntimeError("failed")
        ):
            with self.assertLogs("libdotfiles.packages", level="ERROR"):
                self.assertFalse(try_install("example"))

    def test_failed_package_name_does_not_block_later_attempts(self) -> None:
        with patch(
            "libdotfiles.packages.install",
            side_effect=[RuntimeError("not available"), True],
        ) as required_install:
            with self.assertLogs("libdotfiles.packages", level="ERROR"):
                self.assertFalse(try_install("arch-name"))
            self.assertTrue(try_install("ubuntu-name"))
        self.assertEqual(required_install.call_count, 2)

    def test_installed_package_is_not_reinstalled(self) -> None:
        installer = Mock()
        installer.has_installed.return_value = True
        with patch("libdotfiles.packages.INSTALLERS", [installer]):
            self.assertTrue(install("example"))
        installer.install.assert_not_called()

    def test_removed_apt_package_is_not_installed(self) -> None:
        with patch(
            "libdotfiles.packages.run",
            return_value=subprocess.CompletedProcess(
                [], 0, "deinstall ok config-files"
            ),
        ):
            self.assertFalse(AptPackageInstaller().has_installed("example"))

    def test_fully_installed_apt_package_is_installed(self) -> None:
        with patch(
            "libdotfiles.packages.run",
            return_value=subprocess.CompletedProcess(
                [], 0, "install ok installed"
            ),
        ):
            self.assertTrue(AptPackageInstaller().has_installed("example"))

    def test_held_apt_package_is_still_installed(self) -> None:
        with patch(
            "libdotfiles.packages.run",
            return_value=subprocess.CompletedProcess(
                [], 0, "hold ok installed"
            ),
        ):
            self.assertTrue(AptPackageInstaller().has_installed("example"))

    def test_pip_names_are_normalized_and_package_list_is_cached(self) -> None:
        installer = PipPackageInstaller()
        with patch(
            "libdotfiles.packages.run",
            return_value=subprocess.CompletedProcess(
                [], 0, '[{"name":"Example_Package","version":"1.0"}]'
            ),
        ) as run:
            self.assertTrue(installer.has_installed("example-package"))
            self.assertTrue(installer.has_installed("example.package"))
            self.assertFalse(installer.has_installed("missing"))
        run.assert_called_once()

    def test_pip_list_failure_is_not_treated_as_empty_environment(
        self,
    ) -> None:
        with patch(
            "libdotfiles.packages.run",
            side_effect=subprocess.CalledProcessError(1, ["pip", "list"]),
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                PipPackageInstaller().has_installed("example")
