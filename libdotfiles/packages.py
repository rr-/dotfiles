import json
import logging
import re
from functools import lru_cache
from urllib.error import HTTPError

from libdotfiles.util import has_executable, run

logger = logging.getLogger(__name__)


class PackageInstaller:
    name: str = ""

    @property
    def is_supported(self) -> bool:
        raise NotImplementedError("not implemented")

    def has_installed(self, package: str) -> bool:
        raise NotImplementedError("not implemented")

    def is_available(self, package: str) -> bool:
        raise NotImplementedError("not implemented")

    def install(self, package: str) -> bool:
        raise NotImplementedError("not implemented")


class AptPackageInstaller(PackageInstaller):
    name = "apt"

    @property
    def is_supported(self) -> bool:
        return has_executable("apt")

    def has_installed(self, package: str) -> bool:
        result = run(
            ["dpkg-query", "-W", "-f=${Status}", package],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and result.stdout.endswith(
            " ok installed"
        )

    def is_available(self, package: str) -> bool:
        return (
            run(
                ["apt", "show", package], check=False, capture_output=True
            ).returncode
            == 0
        )

    def install(self, package: str) -> bool:
        return (
            run(
                ["sudo", "-S", "apt", "install", "-y", package], check=False
            ).returncode
            == 0
        )


class PacmanPackageInstaller(PackageInstaller):
    name = "pacman"

    @property
    def is_supported(self) -> bool:
        return has_executable("pacman") and has_executable("sudo")

    def has_installed(self, package: str) -> bool:
        return (
            run(
                ["pacman", "-Q", package], check=False, capture_output=True
            ).returncode
            == 0
        )

    def is_available(self, package: str) -> bool:
        return (
            run(
                ["pacman", "-Si", package], check=False, capture_output=True
            ).returncode
            == 0
        )

    def install(self, package: str) -> bool:
        return (
            run(
                ["sudo", "-S", "pacman", "-S", package, "--noconfirm"],
                check=False,
            ).returncode
            == 0
        )


class PacaurPackageInstaller(PackageInstaller):
    name = "pacaur"

    @property
    def is_supported(self) -> bool:
        return has_executable("pacaur")

    def has_installed(self, package: str) -> bool:
        return (
            run(
                ["pacaur", "-Q", package], check=False, capture_output=True
            ).returncode
            == 0
        )

    def is_available(self, package: str) -> bool:
        return (
            run(
                ["pacaur", "-Ss", package], check=False, capture_output=True
            ).returncode
            == 0
        )

    def install(self, package: str) -> bool:
        return (
            run(
                ["pacaur", "-S", package, "--noconfirm", "--noedit"],
                check=False,
            ).returncode
            == 0
        )


class PipPackageInstaller(PackageInstaller):
    name = "pip"

    @property
    def is_supported(self) -> bool:
        return (
            has_executable("python3")
            and run(
                ["python3", "-m", "pip", "--version"],
                check=False,
                capture_output=True,
            ).returncode
            == 0
        )

    @lru_cache
    def get_installed_packages(self) -> list[tuple[str, str, str | None]]:
        output = run(
            ["python3", "-m", "pip", "list", "--format=json"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        return [
            (item["name"], item["version"], None)
            for item in json.loads(output)
        ]

    def has_installed(self, package: str) -> bool:
        return any(
            re.sub(r"[-_.]+", "-", other_package).lower()
            == re.sub(r"[-_.]+", "-", package).lower()
            for (
                other_package,
                _other_version,
                _other_location,
            ) in self.get_installed_packages()
        )

    def is_available(self, package: str) -> bool:
        import urllib.request

        request = urllib.request.Request(
            f"https://pypi.org/pypi/{package}/json", method="HEAD"
        )
        try:
            with urllib.request.urlopen(request, timeout=30):
                pass
        except HTTPError:
            return False
        else:
            return True

    def install(self, package: str) -> bool:
        command = [
            "python3",
            "-m",
            "pip",
            "install",
            "--user",
            "--break-system-packages",
            package,
        ]
        return run(command, check=False).returncode == 0


INSTALLERS = [cls() for cls in PackageInstaller.__subclasses__()]


def try_install(package: str, method: str | None = None) -> bool:
    """Attempt installation without blocking configuration on package errors."""
    try:
        return install(package, method)
    except Exception as ex:
        logger.error("Error installing %s: %s", package, ex)
        return False


def has_installed(package: str, method: str | None = None) -> bool:
    chosen_installers = _choose_installers(method)
    return any(
        installer.has_installed(package) for installer in chosen_installers
    )


def install(package: str, method: str | None = None) -> bool:
    if has_installed(package, method):
        logger.info("Package %s is already installed.", package)
        return True
    chosen_installers = _choose_installers(method)
    for installer in chosen_installers:
        if installer.is_available(package):
            logger.info(
                "Package %s is available, installing with %s",
                package,
                installer.name,
            )
            if not installer.install(package):
                raise RuntimeError(
                    f"Failed to install {package} with {installer.name}"
                )
            return True
    if method is None:
        raise RuntimeError(
            f"No package manager is capable of installing {package}"
        )
    raise RuntimeError(f"{method} is not capable of installing {package}")


def _choose_installers(method: str | None) -> list[PackageInstaller]:
    if method is None:
        chosen_installers = INSTALLERS
    else:
        chosen_installers = [i for i in INSTALLERS if i.name == method]
    chosen_installers = [i for i in chosen_installers if i.is_supported]
    if not chosen_installers:
        if method is None:
            raise RuntimeError(
                "No package manager is supported on this system!"
            )
        raise RuntimeError(f"{method} is not supported on this system!")
    return chosen_installers
