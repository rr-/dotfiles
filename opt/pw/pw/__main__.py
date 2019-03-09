#!/usr/bin/env python3
import argparse
import sys

from .cmd import *


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help="choose the command", dest="command"
    )
    for cls in Command.__subclasses__():
        instance = cls()
        subparser = subparsers.add_parser(cls.name)
        instance.decorate_parser(subparser)
        subparser.set_defaults(command=instance)
    args = parser.parse_args()
    if not args.command:
        parser.error("no command")
    return args


def main() -> None:
    args = parse_args()
    try:
        args.command.run(args)
    except RuntimeError as ex:
        print(ex, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
