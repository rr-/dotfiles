import abc
import io
import asyncio

import speech_recognition as sr
from bubblesub.model import classproperty
from bubblesub.api.cmd import PluginCommand


async def _work(language, api, logger, line):
    logger.info('line #{} - analyzing'.format(line.number))
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
        logger.warn('line #{}: not recognized'.format(line.number))
    except sr.RequestError as ex:
        logger.error('line #{}: error ({})'.format(line.number, ex))
    else:
        logger.info('line #{}: OK'.format(line.number))
        with api.undo.capture():
            if line.note:
                line.note = line.note + r'\N' + note
            else:
                line.note = note


class SpeechRecognitionCommand(PluginCommand):
    @abc.abstractproperty
    @classproperty
    def language_code(cls):
        raise NotImplementedError('Unknown language code')

    @abc.abstractproperty
    @classproperty
    def language_name(cls):
        raise NotImplementedError('Unknown language name')

    @classproperty
    def name(cls):
        return 'grid/speech-recognition-' + cls.language_code

    @property
    def menu_name(self):
        return 'Speech recognition (&{})'.format(self.language_name)

    @property
    def is_enabled(self):
        return self.api.subs.has_selection \
            and self.api.media.audio.has_audio_source

    async def run(self):
        for line in self.api.subs.selected_lines:
            await _work(self.language_code, self.api, self, line)


def define_cmd(language_code, language_name):
    type(
        'CustomSpeechRecognitionCommand',
        (SpeechRecognitionCommand, PluginCommand),
        {'language_code': language_code, 'language_name': language_name})


def define_cmds():
    for language_code, language_name in [
            ('ja', 'Japanese'),
            ('de', 'German'),
            ('fr', 'French'),
            ('it', 'Italian'),
            ('auto', 'auto')]:
        define_cmd(language_code, language_name)


define_cmds()
