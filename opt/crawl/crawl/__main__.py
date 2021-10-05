#!/usr/bin/env python3.9
import argparse

import crawl.cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="crawl")
    subparsers = parser.add_subparsers()
    for command_cls in crawl.cmd.BaseCommand.__subclasses__():
        subparser = subparsers.add_parser(command_cls.name)
        command = command_cls()
        command.decorate_parser(subparser)
        subparser.set_defaults(command=command)
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.error("no command specified")
    return args


def main() -> None:
    args = parse_args()
    try:
        args.command.run(args)
    except InterruptedError:
        print("exiting due to user interrupt")


if __name__ == "__main__":
    main()
