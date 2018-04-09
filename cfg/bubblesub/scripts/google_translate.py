import abc
import asyncio

import googletrans
from bubblesub.model import classproperty
from bubblesub.api.cmd import PluginCommand


async def _work(language, api, logger, line):
    logger.info('line #{} - analyzing'.format(line.number))
    try:
        def recognize():
            translator = googletrans.Translator()
            return translator.translate(line.note, src=language, dest='en')

        # don't clog the UI thread
        result = (
            await asyncio.get_event_loop().run_in_executor(None, recognize))
    except Exception as ex:
        logger.error('line #{}: error ({})'.format(line.number, ex))
    else:
        logger.info('line #{}: OK'.format(line.number))
        with api.undo.capture():
            if line.text:
                line.text = line.text + r'\N' + result.text
            else:
                line.text = result.text


class GoogleTranslateCommand(PluginCommand):
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
        return 'grid/google-translate-' + cls.language_code

    @property
    def menu_name(self):
        return 'Google Translate (&{})'.format(self.language_name)

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            await _work(self.language_code, self.api, self, line)


def define_cmd(language_code, language_name):
    type(
        'CustomGoogleTranslateCommand',
        (GoogleTranslateCommand, PluginCommand),
        {'language_code': language_code, 'language_name': language_name})


def define_cmds():
    for language_code, language_name in [
            ('auto', 'auto'),
            ('ja', 'Japanese')]:
        define_cmd(language_code, language_name)


define_cmds()
