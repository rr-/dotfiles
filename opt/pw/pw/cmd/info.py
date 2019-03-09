import argparse

from pw.cmd.base import Command
from pw.db import PasswordDoesNotExist, database


class InfoPasswordCommand(Command):
    name = "info"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name")
        parser.add_argument("-p", "--print-password", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            if args.name not in db:
                raise PasswordDoesNotExist
            for key, value in db[args.name].items():
                if key != "pass" or args.print_password:
                    print(f"{key}: {value}")
