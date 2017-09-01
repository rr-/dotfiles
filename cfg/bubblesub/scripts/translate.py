import io
import asyncio
import googletrans
import bubblesub.util
from bubblesub.api.cmd import PluginCommand


async def _work(language, api, logger, line):
    logger.info('line #{} - analyzing'.format(line.number))
    try:
        def recognize():
            translator = googletrans.Translator()
            return translator.translate(line.note, src=language, dest='en')

        # don't clog the UI thread
        result = await asyncio.get_event_loop().run_in_executor(None, recognize)

    except sr.UnknownValueError:
        logger.warn('line #{}: not recognized'.format(line.number))
    except sr.RequestError as ex:
        logger.error('line #{}: error ({})'.format(line.number, ex))
    else:
        logger.info('line #{}: OK'.format(line.number))
        if line.text:
            line.text = line.text + r'\N' + result.text
        else:
            line.text = result.text


class GoogleTranslateCommand:
    @bubblesub.util.classproperty
    def language(self):
        raise NotImplementedError('Unknown language')

    @bubblesub.util.classproperty
    def name(self):
        return 'grid/google-translate-' + self.language

    @property
    def menu_name(self):
        return 'Google Translate ({})'.format(self.language)

    def enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            await _work(self.language, self.api, self, line)


class JapaneseCommand(GoogleTranslateCommand, PluginCommand):
    language = 'ja'


class AutoCommand(GoogleTranslateCommand, PluginCommand):
    language = 'auto'
