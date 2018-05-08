import asyncio

import googletrans
from bubblesub.api.cmd import BaseCommand
from bubblesub.opt.menu import MenuCommand
from bubblesub.opt.menu import SubMenu


async def _work(language, api, logger, line):
    logger.info(f'line #{line.number} - analyzing')
    try:
        def recognize():
            translator = googletrans.Translator()
            return translator.translate(line.note, src=language, dest='en')

        # don't clog the UI thread
        result = (
            await asyncio.get_event_loop().run_in_executor(None, recognize)
        )
    except Exception as ex:
        logger.error(f'line #{line.number}: error ({ex})')
    else:
        logger.info(f'line #{line.number}: OK')
        with api.undo.capture():
            if line.text:
                line.text = line.text + r'\N' + result.text
            else:
                line.text = result.text


class GoogleTranslateCommand(BaseCommand):
    name = 'plugin/google-translate'

    def __init__(self, api, language_code, language_name):
        super().__init__(api)
        self._language_code = language_code
        self._language_name = language_name

    @property
    def menu_name(self):
        return f'&{self._language_name}'

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_events:
            await _work(self._language_code, self.api, self, line)


def register(cmd_api):
    cmd_api.register_plugin_command(
        GoogleTranslateCommand,
        SubMenu(
            '&Translate',
            [
                MenuCommand(GoogleTranslateCommand.name, 'ja', 'Japanese'),
                MenuCommand(GoogleTranslateCommand.name, 'de', 'German'),
                MenuCommand(GoogleTranslateCommand.name, 'fr', 'French'),
                MenuCommand(GoogleTranslateCommand.name, 'it', 'Italian'),
                MenuCommand(GoogleTranslateCommand.name, 'auto', 'auto')
            ]
        )
    )
