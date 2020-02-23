import argparse

from pw.cmd.base import Command
from pw.common import get_random_pass


class GetRandomPasswordCommand(Command):
    name = "generate"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-l", "--length", default=25, type=int)

    def run(self, args: argparse.Namespace) -> None:
        print(get_random_pass(args.length))
