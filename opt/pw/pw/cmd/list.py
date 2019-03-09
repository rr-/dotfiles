import argparse

from pw.cmd.base import Command
from pw.db import database


class ListPasswordsCommand(Command):
    name = "list"

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            print("\n".join(sorted(db.keys())))
