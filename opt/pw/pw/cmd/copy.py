import argparse
import subprocess
import time

from pw.cmd.base import Command
from pw.db import PasswordDoesNotExist, database


class CopyPasswordCommand(Command):
    name = "copy"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name")
        parser.add_argument("--wait", type=int, default=5)

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            if args.name not in db:
                raise PasswordDoesNotExist
            subprocess.run(
                ["xclip"], input=db[args.name]["pass"], encoding="ascii"
            )
            print(f"Clipboard updated, waiting {args.wait} second to clear")
            time.sleep(args.wait)
            subprocess.run(["xclip"], input=b"\x00")
