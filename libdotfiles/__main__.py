#!/usr/bin/env python3
import os
import typing as T
from pathlib import Path

import click

from libdotfiles import logging
from libdotfiles.util import REPO_ROOT_DIR


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string."""

    def convert(self, value: T.Any, param: T.Any, ctx: T.Any) -> T.Any:
        return Path(super().convert(value, param, ctx))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    logging.setup_colored_logs(fmt="[%(asctime)s/%(name)s] %(message)s")


@cli.command()
@click.argument(
    "paths",
    type=PathPath(exists=True, dir_okay=True, file_okay=False),
    nargs=-1,
)
def install(paths: T.List[Path]) -> None:
    """Install given module."""
    original_dir = os.getcwd()
    for module_path in paths:
        module_path = REPO_ROOT_DIR / module_path
        os.chdir(module_path)
        scope = {}
        exec((module_path / "install.py").read_text(), scope)
        scope["run"]()
        os.chdir(original_dir)


def init() -> None:
    if __name__ == "__main__":
        cli()


init()
