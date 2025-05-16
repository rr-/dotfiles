import argparse

from photomgr.commands.base import BaseCommand  # noqa


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


if __name__ == "__main__":
    main()
