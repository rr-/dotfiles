import argparse

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection

START = "{\\fnArial}\N{EIGHTH NOTE}{\\fn}  "
END = "  {\\fnArial}\N{EIGHTH NOTE}{\\fn}"


class DecorateSongCommand(BaseCommand):
    names = ["decorate-song"]
    help_text = "Aligns subtitles to video frames."

    @property
    def is_enabled(self):
        return self.args.target.makes_sense

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
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
                    START + sub.text.replace(r"\N", fr"{END}\N{START}") + END
                )


COMMANDS = [DecorateSongCommand]
MENU = [MenuCommand("&Decorate song with notes", "decorate-song")]
