import glob
import logging
import os
import shlex
import shutil
import subprocess
import urllib.request
from pathlib import Path
from subprocess import PIPE, Popen, call
from typing import Any, Optional

import __main__

logger = logging.getLogger(__name__)

LIBDOTFILES_DIR = Path(__file__).parent.absolute()
REPO_ROOT_DIR = LIBDOTFILES_DIR.parent
HOME_DIR = Path("~").expanduser()
PKG_DIR = Path(__main__.__file__).parent


def run(command: list[Any], **kwargs: Any) -> Any:
    logger.info("Running %r...", shlex.join(map(str, command)))
    return subprocess.run(command, **kwargs)


def run_silent(*args: Any, **kwargs: Any) -> tuple[bool, str, str]:
    proc = Popen(stdout=PIPE, stderr=PIPE, *args, **kwargs)
    out, err = proc.communicate()
    try:
        out, err = out.decode("utf8"), err.decode("utf8")
    except UnicodeDecodeError:
        pass
    return (proc.returncode == 0, out, err)


def run_verbose(*args: Any, **kwargs: Any) -> bool:
    return call(*args, **kwargs) == 0


def has_executable(program: str) -> bool:
    return shutil.which(program) is not None


def download(url: str, path: Path, overwrite: bool = False) -> None:
    create_dir(path.parent)
    if overwrite or not path.exists():
        logger.info("Downloading %r into %r...", url, path)
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "mozilla")
        request.add_header("Referer", url)
        response = urllib.request.urlopen(request)
        with path.open("wb") as handle:
            handle.write(response.read())


def create_file(
    path: Path, content: Optional[str] = None, overwrite: bool = False
) -> None:
    create_dir(path.parent)
    if overwrite or not os.path.exists(path):
        logger.info("Creating file %r...", path)
        with path.open("w", encoding="utf-8") as handle:
            if content:
                handle.write(content)


def create_dir(path: Path) -> None:
    if not path.exists():
        logger.info("Creating directory %r...", path)
        path.mkdir(parents=True)


def create_symlink(source: Path, target: Path) -> None:
    _remove_symlink(target)
    if target.exists() and not target.is_symlink():
        raise RuntimeError(
            f"Target file {target} exists and is not a symlink."
        )
    logger.info("Linking %r to %r...", source, target)
    create_dir(target.parent)
    os.symlink(source, target)


def create_symlinks(items: list[tuple[Path, Path]]) -> None:
    for (source, target) in items:
        create_symlink(source, target)


def _remove_symlink(path: Path) -> None:
    if path.is_symlink():
        logger.info("Removing old symlink %r...", path)
        path.unlink()


def distro_name() -> str:
    for line in Path("/etc/os-release").read_text().splitlines():
        key, value = line.split("=", 1)
        key = key.lower()
        if key == "id":
            return value.strip('"')
    return "unknown"
