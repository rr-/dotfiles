import argparse
from getpass import getpass

from pw.cmd.base import Command
from pw.common import DEFAULT_WAIT, get_random_pass, set_clipboard_for
from pw.db import database


class SetPasswordCommand(Command):
    name = "set"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name")
        parser.add_argument("-u", "--user")
        parser.add_argument("--copy", action="store_true")
        parser.add_argument("--wait", type=int, default=DEFAULT_WAIT)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-r", "--random", action="store_true")
        group.add_argument("-m", "--manual", action="store_true")

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            if args.name not in db:
                db[args.name] = {"user": "", "pass": ""}

            if args.user:
                db[args.name]["user"] = args.user
                print("User name set")

            if args.manual:
                db[args.name]["pass"] = getpass()
                print("Password set")
            elif args.random:
                db[args.name]["pass"] = get_random_pass()
                print("Password set")

            if args.copy:
                set_clipboard_for(db[args.name]["pass"], args.wait)
