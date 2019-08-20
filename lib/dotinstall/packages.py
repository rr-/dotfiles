import logging
import re
import sys
import typing as T

from dotinstall import util

logger = logging.getLogger(__name__)


class PackageInstaller:
    @property
    def name(self) -> str:
        raise NotImplementedError("not implemented")

    @property
    def is_supported(self) -> bool:
        raise NotImplementedError("not implemented")

    def has_installed(self, package: str) -> bool:
        raise NotImplementedError("not implemented")

    def is_available(self, package: str) -> bool:
        raise NotImplementedError("not implemented")

    def install(self, package: str) -> bool:
        raise NotImplementedError("not implemented")


class CygwinPackageInstaller(PackageInstaller):
    name = "cygwin"

    @property
    def is_supported(self) -> bool:
        return util.has_executable("apt-cyg")

    def has_installed(self, package: str) -> bool:
        return (
            len(util.run_silent(["apt-cyg", "list", "^%s$" % package])[1]) > 0
        )

    def is_available(self, package: str) -> bool:
        return (
            len(util.run_silent(["apt-cyg", "listall", "^%s$" % package])[1])
            > 0
        )

    def install(self, package: str) -> bool:
        return util.run_verbose(["apt-cyg", "install", package])


class AptPackageInstaller(PackageInstaller):
    name = "apt"

    @property
    def is_supported(self) -> bool:
        return util.has_executable("apt")

    def has_installed(self, package: str) -> bool:
        return util.run_silent(["dpkg", "-l", package])[0]

    def is_available(self, package: str) -> bool:
        return util.run_silent(["apt", "show", package])[0]

    def install(self, package: str) -> bool:
        return util.run_verbose(["sudo", "-S", "apt", "install", package])


class PacmanPackageInstaller(PackageInstaller):
    name = "pacman"

    @property
    def is_supported(self) -> bool:
        return util.has_executable("pacman") and util.has_executable("sudo")

    def has_installed(self, package: str) -> bool:
        return util.run_silent(["pacman", "-Q", package])[0]

    def is_available(self, package: str) -> bool:
        return util.run_silent(["pacman", "-Ss", package])[0]

    def install(self, package: str) -> bool:
        return util.run_verbose(["sudo", "-S", "pacman", "-S", package])


class PacaurPackageInstaller(PackageInstaller):
    name = "pacaur"

    @property
    def is_supported(self) -> bool:
        return util.has_executable("pacaur")

    def has_installed(self, package: str) -> bool:
        return util.run_silent(["pacaur", "-Q", package])[0]

    def is_available(self, package: str) -> bool:
        return util.run_silent(["pacaur", "-Ss", package])[0]

    def install(self, package: str) -> bool:
        return util.run_verbose(
            ["pacaur", "-S", package, "--noconfirm", "--noedit"]
        )


class PipPackageInstaller(PackageInstaller):
    name = "pip"

    def __init__(self) -> None:
        if "cygwin" in sys.platform:
            self.executable = "pip3"
        else:
            self.executable = "pip"

    @property
    def is_supported(self) -> bool:
        return util.has_executable(self.executable)

    def has_installed(self, package: str) -> bool:
        return (
            re.search(
                "^" + re.escape(package) + r"($|\s)",
                util.run_silent([self.executable, "list"])[1],
                re.MULTILINE,
            )
            is not None
        )

    def is_available(self, package: str) -> bool:
        return (
            re.search(
                "^" + re.escape(package) + r"($|\s)",
                util.run_silent([self.executable, "search", package])[1],
                re.MULTILINE,
            )
            is not None
        )

    def install(self, package: str) -> bool:
        command = [self.executable, "install", "--user", package]
        return util.run_verbose(command)


INSTALLERS = [cls() for cls in PackageInstaller.__subclasses__()]


def try_install(package: str, method: T.Optional[str] = None) -> bool:
    try:
        return install(package, method)
    except Exception as ex:
        logger.info("Error installing %s: %s", package, ex)
        return False


def has_installed(package: str, method: T.Optional[str] = None) -> bool:
    chosen_installers = _choose_installers(method)
    return any(
        installer.has_installed(package) for installer in chosen_installers
    )


def install(package: str, method: T.Optional[str] = None) -> bool:
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


def _choose_installers(method: T.Optional[str]) -> T.List[PackageInstaller]:
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
