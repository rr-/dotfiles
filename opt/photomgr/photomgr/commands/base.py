import argparse


class BaseCommand:
    name: str = NotImplemented

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        return

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError("not implemented")
