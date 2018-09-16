import argparse
import asyncio
import io

import speech_recognition as sr
from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.ass.event import Event
from bubblesub.opt.menu import MenuCommand
from bubblesub.opt.menu import SubMenu


async def _work(language: str, api: Api, line: Event) -> None:
    api.log.info(f'line #{line.number} - analyzing')
    recognizer = sr.Recognizer()
    try:
        def recognize():
            with io.BytesIO() as handle:
                api.media.audio.save_wav(handle, [(line.start, line.end)])
                handle.seek(0, io.SEEK_SET)
                with sr.AudioFile(handle) as source:
                    audio = recognizer.record(source)
            return recognizer.recognize_google(audio, language=language)

        # don't clog the UI thread
        note = await asyncio.get_event_loop().run_in_executor(None, recognize)
    except sr.UnknownValueError:
        api.log.warn(f'line #{line.number}: not recognized')
    except sr.RequestError as ex:
        api.log.error(f'line #{line.number}: error ({ex})')
    else:
        api.log.info(f'line #{line.number}: OK')
        with api.undo.capture():
            if line.note:
                line.note = line.note + r'\N' + note
            else:
                line.note = note


class SpeechRecognitionCommand(BaseCommand):
    names = ['google-speech-recognition']
    help_text = (
        'Puts results of Google speech recognition '
        'for selected subtitles into their notes.'
    )

    @property
    def is_enabled(self):
        return self.api.subs.has_selection \
            and self.api.media.audio.has_audio_source

    async def run(self):
        for line in self.api.subs.selected_events:
            await _work(self.args.code, self.api, line)

    @staticmethod
    def _decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('code', help='language code')


COMMANDS = [SpeechRecognitionCommand]
MENU = [
    SubMenu(
        '&Speech recognition',
        [
            MenuCommand('&Japanese', '/google-speech-recognition ja'),
            MenuCommand('&German', '/google-speech-recognition de'),
            MenuCommand('&French', '/google-speech-recognition fr'),
            MenuCommand('&Italian', '/google-speech-recognition it'),
            MenuCommand('&Auto', '/google-speech-recognition auto')
        ]
    )
]
