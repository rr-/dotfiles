import argparse
import asyncio
import typing as T
from subprocess import PIPE, run

import ass_tag_parser
from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand, SubMenu
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.fmt.ass.event import AssEvent


def translate(
    text: str, engine: str, source_code: str, target_code: str
) -> str:
    if not text.strip():
        return ""

    args = ["trans", "-b"]
    args += ["-e", engine]
    args += ["-s", source_code]
    args += ["-t", target_code]
    args += [text]
    result = run(args, check=True, stdout=PIPE, stderr=PIPE)
    response = result.stdout.decode().strip()
    if not response:
        raise ValueError("error")
    return response


def preprocess(chunk: str) -> str:
    return chunk.replace("\n", " ").replace("\\N", " ")


def postprocess(chunk: str) -> str:
    return (
        chunk.replace("...", "…")
        .replace(" !", "!")
        .replace(" ?", "?")
        .replace(" …", "…")
    )


def collect_text_chunks(events: T.List[AssEvent]) -> str:
    for event in events:
        text = event.note
        try:
            ass_line = ass_tag_parser.parse_ass(text)
        except ass_tag_parser.ParseError as ex:
            if text:
                yield text
        else:
            for item in ass_line:
                if isinstance(item, ass_tag_parser.AssText) and item.text:
                    yield item.text


def put_text_chunks(events: T.List[AssEvent], chunks: T.List[str]) -> str:
    for event in events:
        text = event.note
        try:
            ass_line = ass_tag_parser.parse_ass(text)
        except ass_tag_parser.ParseError as ex:
            text = chunks.pop(0)
        else:
            text = ""
            for item in ass_line:
                if isinstance(item, ass_tag_parser.AssText) and item.text:
                    text += chunks.pop(0)
                else:
                    text += item.meta.text
        if event.text:
            event.text += "\\N" + text
        else:
            event.text = text


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

    def run_in_background(self, subs: T.List[AssEvent]) -> None:
        chunks = list(collect_text_chunks(subs))

        lines = "\n".join(map(preprocess, chunks))

        try:
            translated_lines = translate(
                lines,
                self.args.engine,
                self.args.source_code,
                self.args.target_code,
            )
        except ValueError as ex:
            self.api.log.error(f"error ({ex})")
            return

        translated_chunks = list(
            map(postprocess, translated_lines.split("\n"))
        )

        if len(translated_chunks) != len(chunks):
            self.api.log.error(f"mismatching number of chunks")
            return

        self.api.log.info("OK")

        with self.api.undo.capture():
            put_text_chunks(subs, translated_chunks)

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
            "-e",
            "--engine",
            help="engine to use",
            choices=["bing", "google", "yandex"],
            default="google",
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
