import io
import asyncio

import speech_recognition as sr
from bubblesub.api.cmd import BaseCommand
from bubblesub.opt.menu import MenuCommand
from bubblesub.opt.menu import SubMenu


async def _work(language, api, logger, line):
    logger.info(f'line #{line.number} - analyzing')
    recognizer = sr.Recognizer()
    try:
        def recognize():
            with io.BytesIO() as handle:
                api.media.audio.save_wav(handle, line.start, line.end)
                handle.seek(0, io.SEEK_SET)
                with sr.AudioFile(handle) as source:
                    audio = recognizer.record(source)
            return recognizer.recognize_google(audio, language=language)

        # don't clog the UI thread
        note = await asyncio.get_event_loop().run_in_executor(None, recognize)
    except sr.UnknownValueError:
        logger.warn(f'line #{line.number}: not recognized')
    except sr.RequestError as ex:
        logger.error(f'line #{line.number}: error ({ex})')
    else:
        logger.info(f'line #{line.number}: OK')
        with api.undo.capture():
            if line.note:
                line.note = line.note + r'\N' + note
            else:
                line.note = note


class SpeechRecognitionCommand(BaseCommand):
    name = 'plugin/speech-recognition'

    def __init__(self, api, language_code, language_name):
        super().__init__(api)
        self._language_code = language_code
        self._language_name = language_name

    @property
    def menu_name(self):
        return f'&{self._language_name}'

    @property
    def is_enabled(self):
        return self.api.subs.has_selection \
            and self.api.media.audio.has_audio_source

    async def run(self):
        for line in self.api.subs.selected_lines:
            await _work(self._language_code, self.api, self, line)


def register(cmd_api):
    cmd_api.register_plugin_command(
        SpeechRecognitionCommand,
        SubMenu(
            '&Speech recognition',
            [
                MenuCommand(SpeechRecognitionCommand.name, 'ja', 'Japanese'),
                MenuCommand(SpeechRecognitionCommand.name, 'de', 'German'),
                MenuCommand(SpeechRecognitionCommand.name, 'fr', 'French'),
                MenuCommand(SpeechRecognitionCommand.name, 'it', 'Italian'),
                MenuCommand(SpeechRecognitionCommand.name, 'auto', 'auto')
            ]
        )
    )
