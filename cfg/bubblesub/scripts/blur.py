import argparse
import typing as T

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection


def smart_float(value: T.Union[int, float, None]) -> str:
    if value is None:
        return ""
    return "{}".format(float(value)).rstrip("0").rstrip(".")


class DecorateSongCommand(BaseCommand):
    names = ["blur"]
    help_text = "Blur selected subtitles."

    @property
    def is_enabled(self):
        return self.args.target.makes_sense

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-a", "--amount", help="amount to blur", type=float, default=0.75
        )
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )

    async def run(self):
        with self.api.undo.capture():
            for sub in await self.args.target.get_subtitles():
                sub.text = (
                    r"{\blur" + smart_float(self.args.amount) + "}" + sub.text
                ).replace("}{", "")


COMMANDS = [DecorateSongCommand]
MENU = [MenuCommand("&Blur selected subtitles", "blur")]
