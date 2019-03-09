import abc
import argparse


class Command:
    name = "..."

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    @abc.abstractmethod
    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError("not implemented")
