import argparse

from photomgr.commands.base import BaseCommand  # noqa
from photomgr.commands.copy_raws import CopyRawsCommand  # noqa
from photomgr.commands.find_missing_raws import FindMissingRawsCommand  # noqa


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    for command_cls in BaseCommand.__subclasses__():
        group = subparsers.add_parser(command_cls.name)
        command = command_cls()
        command.decorate_parser(group)
        group.set_defaults(command=command)

    args = parser.parse_args()
    args.command.run(args)
