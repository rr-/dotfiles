import argparse
import sys
from getpass import getpass

from pw.cmd.base import Command
from pw.db import read_database, write_database


class ChangeMasterPasswordCommand(Command):
    name = "cmp"

    def run(self, args: argparse.Namespace) -> None:
        key = getpass("Old master password: ")
        db = read_database(key)

        while True:
            key = getpass("New master password: ")
            key2 = getpass("Repeat master password: ")
            if key == key2:
                break
            print("Passwords don't match", file=sys.stderr)

        write_database(key, db)
