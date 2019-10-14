import argparse

from pw.cmd.base import Command
from pw.common import DEFAULT_WAIT, set_clipboard_for
from pw.db import PasswordDoesNotExist, database


class CopyPasswordCommand(Command):
    name = "copy"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name")
        parser.add_argument("--wait", type=int, default=DEFAULT_WAIT)

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            if args.name not in db:
                raise PasswordDoesNotExist
            set_clipboard_for(db[args.name]["pass"], args.wait)
