import argparse
from pathlib import Path

from photomgr.commands.base import BaseCommand
from photomgr.common import JPEG_SUFFIXES
from photomgr.filesystem import find_jpegs, find_matching_path


class CopyJpegsCommand(BaseCommand):
    name = "copy-jpegs"
    description = (
        "Copy JPEG files from a given directory for local examination. "
        "Does not copy RAW files."
    )

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-d", "--dry-run", action="store_true")
        parser.add_argument("-s", "--source", type=Path)
        parser.add_argument("-t", "--target", type=Path, default=Path("."))
        parser.add_argument("-r", "--recursive", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        jpeg_paths = list(find_jpegs(args.source, recursive=args.recursive))
        print("Found", len(jpeg_paths), "jpeg files")

        for i, path in enumerate(jpeg_paths):
            rel_path = path.relative_to(args.source)
            target_dir = args.target / path.parent.relative_to(args.source)
            print(f"{rel_path} ({i/len(jpeg_paths):.02%})... ", end="")

            if target_path := find_matching_path(
                rel_path, target_dir, suffixes=JPEG_SUFFIXES
            ):
                print(f"JPEG already copied: {target_path}")
            else:
                target_path = target_dir / path.name
                print(f"Copying {path} to {target_path}")
                if not args.dry_run:
                    target_path.parent.mkdir(exist_ok=True, parents=True)
                    target_path.write_bytes(path.read_bytes())
