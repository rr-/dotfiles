import argparse


class BaseCommand:
    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, args: argparse.Namespace) -> None:
        pass
