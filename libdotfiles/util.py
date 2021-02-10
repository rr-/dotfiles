import glob
import logging
import os
import shutil
import typing as T
import urllib.request
from pathlib import Path
from subprocess import PIPE, Popen, call

logger = logging.getLogger(__name__)

LIBDOTFILES_DIR = Path(__file__).parent.absolute()
REPO_ROOT_DIR = LIBDOTFILES_DIR.parent


def run_silent(*args: T.Any, **kwargs: T.Any) -> T.Tuple[bool, str, str]:
    proc = Popen(stdout=PIPE, stderr=PIPE, *args, **kwargs)
    out, err = proc.communicate()
    try:
        out, err = out.decode("utf8"), err.decode("utf8")
    except UnicodeDecodeError:
        pass
    return (proc.returncode == 0, out, err)


def run_verbose(*args: T.Any, **kwargs: T.Any) -> bool:
    return call(*args, **kwargs) == 0


def has_executable(program: str) -> bool:
    return shutil.which(program) is not None


def assert_has_executable(program: str) -> None:
    if not has_executable(program):
        raise RuntimeError(f"{program} not installed, cannot proceed")


def expand_path(path: str, source: T.Optional[str] = None) -> str:
    is_dir = path.endswith("/") or path.endswith("\\")
    target = os.path.abspath(os.path.expanduser(path))
    if is_dir and source:
        target = os.path.join(target, os.path.basename(source))
    return target


def abs_path(path: str) -> str:
    return os.path.abspath(expand_path(path))


def find(path: str) -> T.Iterable[str]:
    path = abs_path(path)
    if os.path.isdir(path):
        return glob.glob(os.path.join(path, "*"))
    return glob.glob(path)


def download(url: str, path: str, overwrite: bool = False) -> None:
    path = expand_path(path)
    if os.path.isdir(path):
        path = os.path.join(path, os.path.basename(url))
    create_dir(os.path.dirname(path))
    if overwrite or not os.path.exists(path):
        logger.info("Downloading %r into %r...", url, path)
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "mozilla")
        request.add_header("Referer", url)
        response = urllib.request.urlopen(request)
        with open(path, "wb") as handle:
            handle.write(response.read())


def exists(path: str) -> bool:
    path = expand_path(path)
    return os.path.exists(path)


def create_file(
    path: str, content: T.Optional[str] = None, overwrite: bool = False
) -> None:
    path = expand_path(path)
    dir_path = os.path.dirname(path)
    create_dir(dir_path)
    if overwrite or not os.path.exists(path):
        logger.info("Creating file %r...", path)
        with open(path, "w") as handle:
            if content:
                handle.write(content)


def create_dir(path: str) -> None:
    path = expand_path(path)
    if not os.path.exists(path):
        logger.info("Creating directory %r...", path)
        os.makedirs(path)


def copy_file(source: str, target: str) -> None:
    source = expand_path(source)
    target = expand_path(target, source)
    _remove_symlink(target)
    logger.info("Copying %r to %r...", source, target)
    create_dir(os.path.dirname(target))
    shutil.copy(source, target)


def create_symlink(source: str, target: str) -> None:
    source = expand_path(source)
    target = expand_path(target, source)
    _remove_symlink(target)
    if os.path.exists(target):
        raise RuntimeError(
            f"Target file {target} exists and is not a symlink."
        )
    logger.info("Linking %r to %r...", source, target)
    create_dir(os.path.dirname(target))
    os.symlink(source, target)


def concat_files(
    sources: T.List[str], target: str, comment_fmt: T.Optional[str] = None
) -> None:
    sources = [os.path.abspath(os.path.expanduser(path)) for path in sources]
    target = os.path.expanduser(target)
    _remove_symlink(target)
    create_dir(os.path.dirname(target))

    logger.info("Concatenating %s to %s...", sources, target)
    with open(target, "w") as target_handle:
        if comment_fmt:
            print(comment_fmt % "DO NOT EDIT THIS FILE", file=target_handle)
            print(
                comment_fmt
                % "This file was concatenated by dotfiles utility.",
                file=target_handle,
            )
            print(
                comment_fmt % "All changes in this file will not be retained.",
                file=target_handle,
            )
            print(file=target_handle)

        for source in sources:
            if comment_fmt:
                print(
                    comment_fmt
                    % "Concatenated file %s of %s from: %s"
                    % (sources.index(source) + 1, len(sources), source),
                    file=target_handle,
                )
            print(Path(source).read_text(), file=target_handle)


def _remove_symlink(path: str) -> None:
    if os.path.islink(path):
        logger.info("Removing old symlink %r...", path)
        os.unlink(path)


def distro_name() -> str:
    for line in Path("/etc/os-release").read_text().splitlines():
        key, value = line.split("=", 1)
        key = key.lower()
        if key == "id":
            return value.strip('"')
    return "unknown"
