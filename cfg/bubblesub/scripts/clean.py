import argparse
import re

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection


def fix_text(text: str) -> str:
    text = text.replace("\\N", "\n")  # convert newlines

    text = text.replace("}{", "")  # disjoint ASS tags
    text = re.sub(r"{\\[bius][01]?}$", "", text)  # dangling ASS tags
    text = re.sub("^- ", "– ", text, flags=re.M)  # bad dalogues dash
    text = text.strip()  # extra whitespace
    text = text.replace("\n ", "\n")  # whitespace after line breaks
    text = text.replace(" \n", "\n")  # whitespace before line breaks
    text = text.replace("...", "…")  # proper ellipsis

    text = text.replace("\n", "\\N")  # restore newlines
    return text


class CleanCommand(BaseCommand):
    names = ["clean"]
    help_text = "Clean subtitles from random garbage."

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
        changed = 0
        with self.api.undo.capture():
            for sub in await self.args.target.get_subtitles():
                text = fix_text(sub.text)
                if text != sub.text:
                    sub.text = text
                    changed += 1
        self.api.log.info(f'fixed {changed} lines')


COMMANDS = [CleanCommand]
MENU = [MenuCommand("&Clean", "clean")]
