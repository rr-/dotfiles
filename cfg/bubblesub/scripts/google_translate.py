import argparse
import asyncio

import googletrans
from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.ass.event import Event
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.opt.menu import MenuCommand
from bubblesub.opt.menu import SubMenu


async def _work(language: str, api: Api, sub: Event) -> None:
    api.log.info(f"line #{sub.number} - analyzing")
    try:

        def recognize():
            translator = googletrans.Translator()
            return translator.translate(
                sub.note.replace("\\N", "\n"), src=language, dest="en"
            )

        # don't clog the UI thread
        result = await asyncio.get_event_loop().run_in_executor(
            None, recognize
        )
    except Exception as ex:
        api.log.error(f"line #{sub.number}: error ({ex})")
    else:
        api.log.info(f"line #{sub.number}: OK")
        with api.undo.capture():
            if sub.text:
                sub.text = sub.text + r"\N" + result.text
            else:
                sub.text = result.text


class GoogleTranslateCommand(BaseCommand):
    names = ["tl", "google-translate"]
    help_text = "Puts results of Google translation into selected subtitles."

    @property
    def is_enabled(self):
        return self.args.target.makes_sense

    async def run(self):
        for sub in await self.args.target.get_subtitles():
            await _work(self.args.code, self.api, sub)

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )
        parser.add_argument("code", help="language code")


COMMANDS = [GoogleTranslateCommand]
MENU = [
    SubMenu(
        "&Translate",
        [
            MenuCommand("&Japanese", "tl ja"),
            MenuCommand("&German", "tl de"),
            MenuCommand("&French", "tl fr"),
            MenuCommand("&Italian", "tl it"),
            MenuCommand("&Polish", "tl pl"),
            MenuCommand("&Auto", "tl auto"),
        ],
    )
]
