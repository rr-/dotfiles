import argparse
import asyncio

import googletrans
from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.opt.menu import MenuCommand
from bubblesub.opt.menu import SubMenu


async def _work(language, api, line):
    api.log.info(f'line #{line.number} - analyzing')
    try:
        def recognize():
            translator = googletrans.Translator()
            return translator.translate(line.note, src=language, dest='en')

        # don't clog the UI thread
        result = (
            await asyncio.get_event_loop().run_in_executor(None, recognize)
        )
    except Exception as ex:
        api.log.error(f'line #{line.number}: error ({ex})')
    else:
        api.log.info(f'line #{line.number}: OK')
        with api.undo.capture():
            if line.text:
                line.text = line.text + r'\N' + result.text
            else:
                line.text = result.text


class GoogleTranslateCommand(BaseCommand):
    names = ['google-translate']
    help_text = 'Puts results of Google translation into selected subtitles.'

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_events:
            await _work(self.args.code, self.api, line)

    @staticmethod
    def _decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('code', help='language code')


def register(cmd_api):
    cmd_api.register_plugin_command(
        GoogleTranslateCommand,
        SubMenu(
            '&Translate',
            [
                MenuCommand('&Japanese', '/google-translate ja'),
                MenuCommand('&German', '/google-translate de'),
                MenuCommand('&French', '/google-translate fr'),
                MenuCommand('&Italian', '/google-translate it'),
                MenuCommand('&Auto', '/google-translate auto')
            ]
        )
    )
