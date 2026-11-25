import hashlib
import logging
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, create_dir, get_distro_name

VERSION = "0.13.10"
SHA256 = {
    "x86_64": "bf65ac1a0af10f92c522d91ac096c7c0a39657647b155577e7836c2cbbb4526c",
    "aarch64": "14590f644805a6234ffe071154340669e38137f38e60aa9629690119704107d2",
}
BIN_DIR = HOME_DIR / ".local" / "bin"

logger = logging.getLogger(__name__)


def installed_version() -> str | None:
    try:
        result = subprocess.run(
            [BIN_DIR / "uv", "--version"], capture_output=True, text=True
        )
    except OSError:
        return None
    return result.stdout.split()[1] if result.returncode == 0 else None


def install_release() -> None:
    if installed_version() == VERSION:
        logger.info("uv %s is already in %s", VERSION, BIN_DIR)
        return
    machine = platform.machine()
    target = f"uv-{machine}-unknown-linux-gnu"
    url = (
        "https://github.com/astral-sh/uv/releases/download/"
        f"{VERSION}/{target}.tar.gz"
    )
    logger.info("Downloading %s...", url)
    with urllib.request.urlopen(url) as response:
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256[machine]:
        raise RuntimeError(f"{url} has sha256 {digest}, not {SHA256[machine]}")
    create_dir(BIN_DIR)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "uv.tar.gz"
        archive.write_bytes(data)
        with tarfile.open(archive) as tar:
            tar.extractall(tmp, filter="data")
        for name in ["uv", "uvx"]:
            shutil.copy2(Path(tmp) / target / name, BIN_DIR / name)
    logger.info("Installed uv %s into %s", VERSION, BIN_DIR)


def install_uv() -> None:
    if get_distro_name() == "arch":
        try_install("uv")
    else:
        install_release()
