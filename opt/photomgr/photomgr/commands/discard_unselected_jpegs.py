import argparse
from pathlib import Path

from photomgr.commands.base import BaseCommand
from photomgr.filesystem import find_jpegs


class DiscardUnselectedJpegsCommand(BaseCommand):
    name = "discard-unselected-jpegs"
    description = (
        "Discard JPEG files that haven't been selected (eg. do not contain "
        "a `-SEL` string in their filename). Does not touch RAW files."
    )

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-d", "--dry-run", action="store_true")
        parser.add_argument("-t", "--target", type=Path, default=Path("."))
        parser.add_argument("-r", "--recursive", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        jpeg_paths = list(find_jpegs(args.target, recursive=args.recursive))
        print("Found", len(jpeg_paths), "jpeg files")

        for i, path in enumerate(jpeg_paths):
            if "-SEL" not in path.name:
                target_path = path.parent / f"{path.name}~"
                print(f"Renaming {path} to {target_path}")
                if not args.dry_run:
                    path.rename(target_path)
