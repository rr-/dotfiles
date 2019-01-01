import argparse
import asyncio
import concurrent.futures
import typing as T
from subprocess import run

import googletrans

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.ass.event import Event
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.opt.menu import MenuCommand, SubMenu


def retry(func: T.Callable, *args: T.Any, **kwargs: T.Any) -> T.Any:
    max_tries = 3
    for i in range(max_tries - 1):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            pass
    return func(*args, **kwargs)


class GoogleTranslateCommand(BaseCommand):
    names = ["tl", "google-translate"]
    help_text = "Puts results of Google translation into selected subtitles."

    @property
    def is_enabled(self) -> bool:
        return self.args.target.makes_sense

    async def run(self) -> None:
        await asyncio.get_event_loop().run_in_executor(
            None,
            self.run_in_background,
            await self.args.target.get_subtitles(),
        )

    def run_in_background(self, subs: T.List[Event]) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_sub = {
                executor.submit(self.recognize, sub): sub for sub in subs
            }
            completed, non_completed = concurrent.futures.wait(
                future_to_sub, timeout=5
            )

        with self.api.undo.capture():
            for future, sub in future_to_sub.items():
                if future in non_completed:
                    self.api.log.info(f"line #{sub.number}: timeout")
                    continue
                assert future in completed
                try:
                    result = future.result()
                except Exception as ex:
                    self.api.log.error(f"line #{sub.number}: error ({ex})")
                else:
                    self.api.log.info(f"line #{sub.number}: OK")
                    if sub.text:
                        sub.text += r"\N" + result
                    else:
                        sub.text = result

    def recognize(self, sub: Event) -> str:
        self.api.log.info(f"line #{sub.number} - analyzing")
        if self.args.alternative:
            result = run(
                [
                    "trans",
                    "-b",
                    "-s",
                    self.args.source_code,
                    "-t",
                    self.args.target_code,
                    sub.note.replace("\\N", "\n"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        else:
            translator = googletrans.Translator()
            return retry(
                lambda: translator.translate(
                    sub.note.replace("\\N", "\n"),
                    src=self.args.source_code,
                    dest=self.args.target_code,
                ).text
            )

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )
        parser.add_argument(
            "-a",
            "--alternative",
            help="use alternative way to translate subtitles",
            action="store_true",
        )
        parser.add_argument(
            metavar="from", dest="source_code", help="source language code"
        )
        parser.add_argument(
            metavar="to",
            dest="target_code",
            help="target language code",
            nargs="?",
            default="en",
        )


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
            MenuCommand("&Spanish", "tl es"),
            MenuCommand("&Auto", "tl auto"),
        ],
    )
]
