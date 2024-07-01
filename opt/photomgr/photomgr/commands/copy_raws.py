import argparse
from pathlib import Path

from photomgr.commands.base import BaseCommand
from photomgr.filesystem import find_jpegs, find_matching_raw


class CopyRawsCommand(BaseCommand):
    name = "copy-raws"
    description = (
        "Copy RAW files from a given directory for which "
        "corresponding JPEG files have NOT been deleted."
    )

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-d", "--dry-run", action="store_true")
        parser.add_argument("-s", "--source", type=Path)
        parser.add_argument("-t", "--target", type=Path, default=Path("."))
        parser.add_argument("-r", "--recursive", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        jpeg_paths = list(find_jpegs(args.target, recursive=args.recursive))
        print("Found", len(jpeg_paths), "jpeg files")
        for i, jpeg_path in enumerate(jpeg_paths):
            rel_path = jpeg_path.relative_to(args.target)
            raw_dir = args.source / jpeg_path.parent.relative_to(args.target)
            print(f"{rel_path} ({i/len(jpeg_paths):.02%})... ", end="")

            if target_raw_path := find_matching_raw(rel_path, args.target):
                print(f"Raw already copied: {target_raw_path}")
            elif source_raw_path := find_matching_raw(jpeg_path, raw_dir):
                target_raw_path = (
                    args.target
                    / rel_path.parent
                    / (jpeg_path.stem + source_raw_path.suffix)
                )
                assert target_raw_path
                print(f"Copying {source_raw_path} to {target_raw_path}")
                if not args.dry_run:
                    target_raw_path.write_bytes(source_raw_path.read_bytes())
            else:
                print("Unable to find RAW!")
