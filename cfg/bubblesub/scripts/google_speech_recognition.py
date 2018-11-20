import argparse
import asyncio
import concurrent.futures
import io
import typing as T

import speech_recognition as sr

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.ass.event import Event
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.opt.menu import MenuCommand, SubMenu


class SpeechRecognitionCommand(BaseCommand):
    names = ["sr", "google-speech-recognition"]
    help_text = (
        "Puts results of Google speech recognition "
        "for selected subtitles into their notes."
    )

    @property
    def is_enabled(self) -> bool:
        return (
            self.args.target.makes_sense
            and self.api.media.audio.has_audio_source
        )

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
            for future in concurrent.futures.as_completed(future_to_sub):
                sub = future_to_sub[future]
                try:
                    note = future.result()
                except sr.UnknownValueError:
                    self.api.log.warn(f"line #{sub.number}: not recognized")
                except sr.RequestError as ex:
                    self.api.log.error(f"line #{sub.number}: error ({ex})")
                else:
                    self.api.log.info(f"line #{sub.number}: OK")
                    with self.api.undo.capture():
                        if sub.note:
                            sub.note += r"\N" + note
                        else:
                            sub.note = note

    def recognize(self, sub: Event) -> str:
        self.api.log.info(f"line #{sub.number} - analyzing")
        recognizer = sr.Recognizer()
        with io.BytesIO() as handle:
            self.api.media.audio.save_wav(handle, [(sub.start, sub.end)])
            handle.seek(0, io.SEEK_SET)
            with sr.AudioFile(handle) as source:
                audio = recognizer.record(source)
            ret = recognizer.recognize_google(audio, language=self.args.code)
        return ret

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


COMMANDS = [SpeechRecognitionCommand]
MENU = [
    SubMenu(
        "&Speech recognition",
        [
            MenuCommand("&Japanese", "sr ja"),
            MenuCommand("&German", "sr de"),
            MenuCommand("&French", "sr fr"),
            MenuCommand("&Italian", "sr it"),
            MenuCommand("&Auto", "sr auto"),
        ],
    )
]
