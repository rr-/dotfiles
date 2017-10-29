import io
import asyncio
import speech_recognition as sr
import bubblesub.util
from bubblesub.api.cmd import PluginCommand


async def _work(language, api, logger, line):
    logger.info('line #{} - analyzing'.format(line.number))
    recognizer = sr.Recognizer()
    try:
        def recognize():
            with io.BytesIO() as handle:
                api.audio.save_wav(handle, line.start, line.end)
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
        if line.note:
            line.note = line.note + r'\N' + note
        else:
            line.note = note


class SpeechRecognitionCommand:
    @bubblesub.util.classproperty
    def language(self):
        raise NotImplementedError('Unknown language')

    @bubblesub.util.classproperty
    def name(self):
        return 'grid/speech-' + self.language

    @property
    def menu_name(self):
        return 'Speech recognition ({})'.format(self.language)

    @property
    def is_enabled(self):
        return self.api.subs.has_selection and self.api.audio.has_audio_source

    async def run(self):
        for line in self.api.subs.selected_lines:
            await _work(self.language, self.api, self, line)


class JapaneseCommand(SpeechRecognitionCommand, PluginCommand):
    language = 'ja'


class GermanCommand(SpeechRecognitionCommand, PluginCommand):
    language = 'de'


class AutoCommand(SpeechRecognitionCommand, PluginCommand):
    language = 'auto'
