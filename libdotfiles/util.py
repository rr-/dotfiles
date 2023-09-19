import glob
import logging
import os
import shlex
import shutil
import subprocess
import urllib.request
from pathlib import Path
from subprocess import PIPE, CompletedProcess, Popen, call
from typing import Any

import __main__

logger = logging.getLogger(__name__)

LIBDOTFILES_DIR = Path(__file__).parent.absolute()
REPO_ROOT_DIR = LIBDOTFILES_DIR.parent
HOME_DIR = Path("~").expanduser()
PKG_DIR = Path(__main__.__file__).parent


def run(command: list[Any], **kwargs: Any) -> CompletedProcess[str]:
    logger.info("Running %r...", shlex.join(map(str, command)))
    return subprocess.run(command, **kwargs)


def has_executable(program: str) -> bool:
    return shutil.which(program) is not None


def download_file(url: str, path: Path, overwrite: bool = False) -> None:
    create_dir(path.parent)
    if overwrite or not path.exists():
        logger.info("Downloading %r into %s...", url, path)
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "mozilla")
        request.add_header("Referer", url)
        response = urllib.request.urlopen(request)
        with path.open("wb") as handle:
            handle.write(response.read())


def create_file(
    path: Path, content: str | None = None, overwrite: bool = False
) -> None:
    create_dir(path.parent)
    if overwrite or not os.path.exists(path):
        logger.info("Creating file %s...", path)
        with path.open("w", encoding="utf-8") as handle:
            if content:
                handle.write(content)


def create_dir(path: Path) -> None:
    if not path.exists():
        logger.info("Creating directory %s...", path)
        path.mkdir(parents=True)


def create_symlink(source: Path, target: Path) -> None:
    _remove_symlink(target)
    if target.exists() and not target.is_symlink():
        raise RuntimeError(
            f"Target file {target} exists and is not a symlink."
        )
    logger.info("Linking %s to %s...", source, target)
    create_dir(target.parent)
    os.symlink(source, target)


def copy_file(source: Path, target: Path) -> None:
    _remove_symlink(target)
    if target.exists() and not target.is_file():
        raise RuntimeError(f"Target file {target} exists and is not a file.")
    logger.info("Copying %s to %s...", source, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def create_symlinks(items: list[tuple[Path, Path]]) -> None:
    for source, target in items:
        create_symlink(source, target)


def _remove_symlink(path: Path) -> None:
    if path.is_symlink():
        logger.info("Removing old symlink %s...", path)
        path.unlink()


def get_distro_name() -> str:
    for line in Path("/etc/os-release").read_text().splitlines():
        key, value = line.split("=", 1)
        key = key.lower()
        if key == "id":
            return value.strip('"')
    return "unknown"


def current_username() -> str:
    return run(
        ["whoami"], check=True, capture_output=True, text=True
    ).stdout.strip()


def git_clone(repo: str, path: str | Path) -> None:
    target_path = Path(path).absolute()
    if target_path.exists():
        if not (target_path / ".git").exists():
            logger.error(
                "Target directory %s already exists and is not a git repository.",
                target_path,
            )
        remote_url = run(
            ["git", "-C", target_path, "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if remote_url.removesuffix(".git") != repo.removesuffix(".git"):
            logger.error(
                "Target repository %s points to %s, expected %s.",
                target_path,
                remote_url,
                repo,
            )
        return
    run(["git", "clone", repo, target_path], check=True)
