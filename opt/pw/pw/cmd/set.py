import argparse
import random
from getpass import getpass

from pw.cmd.base import Command
from pw.db import database


class SetPasswordCommand(Command):
    name = "set"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name")
        parser.add_argument("-u", "--user")
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
                db[args.name]["pass"] = self.get_random_pass()
                print("Password set")

    @staticmethod
    def get_random_pass(length: int = 32) -> str:
        alpha = "abcdefghijklmnopqrstuvwxyz"
        alpha += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        alpha += "0123456789"
        alpha += ",._-+@%/"
        while True:
            password = "".join(random.choice(alpha) for _ in range(length))
            if not password.startswith(" ") and not password.endswith(" "):
                return password
