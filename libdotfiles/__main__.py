#!/usr/bin/env python3
import importlib
import logging
import os
import sys
import typing as T
from pathlib import Path

import click

LIB_DIR = Path(__file__).parent.absolute()
ROOT_DIR = LIB_DIR.parent


def setup_logger() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s/%(name)s] %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string."""

    def convert(self, value: T.Any, param: T.Any, ctx: T.Any) -> T.Any:
        return Path(super().convert(value, param, ctx))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    setup_logger()


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
        module_path = ROOT_DIR / module_path
        os.chdir(module_path)
        module = importlib.import_module("install")
        module.run()
        os.chdir(original_dir)


def init() -> None:
    if __name__ == "__main__":
        cli()


init()
