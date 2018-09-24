import argparse
import asyncio
import subprocess

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.api.cmd import CommandUnavailable
from bubblesub.cmd.common import Pts
from bubblesub.cmd.common import FancyPath
from bubblesub.opt.menu import MenuCommand
from bubblesub.util import ms_to_str


class SaveVideoSampleCommand(BaseCommand):
    names = ['save-video-sample']
    help_text = (
        'Saves given subtitles to a WEBM file. '
        'Prompts user to choose where to save the file to if the path wasn\'t '
        'specified in the command arguments.'
    )

    @property
    def is_enabled(self) -> bool:
        return self.api.media.video.has_video_source

    async def run(self) -> None:
        start = await self.args.start.get()
        end = await self.args.end.get()
        if end < start:
            end, start = start, end
        if start == end:
            raise CommandUnavailable('nothing to sample')

        assert self.api.media.path
        path = await self.args.path.get_save_path(
            file_filter='Webm Video File (*.webm)',
            default_file_name='video-{}-{}..{}.webm'.format(
                self.api.media.path.name,
                ms_to_str(start),
                ms_to_str(end)
            )
        )

        def create_sample():
            subprocess.run([
                'ffmpeg',
                '-i', self.api.media.path,
                '-y',
                '-ss', ms_to_str(start),
                '-to', ms_to_str(end),
                str(path)
            ])

        # don't clog the UI thread
        self.api.log.info(f'saving video sample to {path}...')
        await asyncio.get_event_loop().run_in_executor(None, create_sample)
        self.api.log.info(f'saved video sample to {path}')

    @staticmethod
    def _decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--start',
            help='where the sample should start',
            type=lambda value: Pts(api, value),
            default='a.s',
        )
        parser.add_argument(
            '--end',
            help='where the sample should end',
            type=lambda value: Pts(api, value),
            default='a.e',
        )
        parser.add_argument(
            '-p', '--path',
            help='path to save the sample to',
            type=lambda value: FancyPath(api, value),
            default='',
        )


COMMANDS = [SaveVideoSampleCommand]
MENU = [MenuCommand('&Create video sample', '/save-video-sample')]
