from collections.abc import Iterable, Sequence
from functools import cache
from pathlib import Path

from photomgr.common import FILENAME_DATE_REGEX, JPEG_SUFFIXES, RAW_SUFFIXES


@cache
def find_files(path: Path, recursive: bool) -> list[Path]:
    result = []
    if path.exists():
        for subpath in path.iterdir():
            if subpath.is_dir():
                if recursive:
                    result.extend(find_files(subpath, recursive=recursive))
            else:
                result.append(subpath)
    return result


def find_jpegs(directory: Path, recursive: bool) -> Iterable[Path]:
    return (
        path
        for path in sorted(find_files(directory, recursive=recursive))
        if path.suffix.lower() in JPEG_SUFFIXES
    )


def case_insensitive_exists(path: Path) -> Path | None:
    for p in find_files(path.parent, recursive=False):
        if p.name.lower() == path.name.lower():
            return p
    return None


def find_matching_path(
    source_path: Path, source_directory: Path, suffixes: Sequence[str]
) -> Path | None:
    stem = source_path.stem
    try_paths = [
        *[source_directory / (stem + suffix) for suffix in suffixes],
        *[
            source_directory / source_path.parent / (stem + suffix)
            for suffix in suffixes
        ],
    ]

    if match := FILENAME_DATE_REGEX.match(source_path.name):
        discriminator = match.group("discriminator")
        try_paths.append(
            source_directory
            / f"{discriminator[0:3]}NCZ_8/DSC_{discriminator[3:]}.NEF"
        )
        try_paths.append(
            source_directory
            / f"{discriminator[0:3]}NCZ_9/DSC_{discriminator[3:]}.NEF"
        )

    for try_path in try_paths:
        if raw_path := case_insensitive_exists(try_path):
            return raw_path

    return None


def find_matching_raw(jpeg_path: Path, parent_dir: Path) -> Path | None:
    return find_matching_path(jpeg_path, parent_dir, suffixes=RAW_SUFFIXES)
