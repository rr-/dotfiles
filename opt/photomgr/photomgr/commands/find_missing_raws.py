import argparse
from pathlib import Path

from photomgr.commands.base import BaseCommand
from photomgr.filesystem import find_jpegs, find_matching_raw


class FindMissingRawsCommand(BaseCommand):
    name = "find-missing-raws"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-t", "--target-dir", type=Path, default=Path("."))
        parser.add_argument("-r", "--recursive", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        for jpeg_path in find_jpegs(args.target_dir, recursive=args.recursive):
            if not find_matching_raw(jpeg_path, jpeg_path.parent):
                print("Missing raw:", jpeg_path)
