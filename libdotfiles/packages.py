import logging
import re
import sys
from functools import lru_cache

from libdotfiles.util import has_executable, run

logger = logging.getLogger(__name__)


class PackageInstaller:
    name: str = NotImplemented

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
        return (
            run(
                ["dpkg", "-l", package], check=False, capture_output=True
            ).returncode
            == 0
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
                ["pacman", "-Ss", package], check=False, capture_output=True
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
        return has_executable("python3")

    @lru_cache
    def get_installed_packages(self) -> list[tuple[str, str, str | None]]:
        output = run(
            ["python3", "-m", "pip", "list"],
            check=False,
            text=True,
            capture_output=True,
        ).stdout
        ret = []
        for line in output.splitlines()[2:]:
            if line:
                result = line.split(maxsplit=2)
                if len(result) == 2:
                    package, version = result
                    location = None
                elif len(result) == 3:
                    package, version, location = result
                else:
                    raise RuntimeError("unexpected output")
                ret.append((package, version, location))
        return ret

    def has_installed(self, package: str) -> bool:
        return any(
            other_package == package
            for (
                other_package,
                _other_version,
                _other_location,
            ) in self.get_installed_packages()
        )

    def is_available(self, package: str) -> bool:
        import urllib.request

        request = urllib.request.Request(
            f"https://pypi.org/project/{package}/", method="HEAD"
        )
        try:
            urllib.request.urlopen(request)
        except urllib.error.HTTPError:
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
            return installer.install(package)
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
