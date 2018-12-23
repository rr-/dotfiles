import argparse

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.opt.menu import MenuCommand


class AlignSubtitlesToVideoFramesCommand(BaseCommand):
    names = ["align-subs-to-video-frames"]
    help_text = "Aligns subtitles to video frames."

    @property
    def is_enabled(self):
        return self.api.media.is_loaded and self.args.target.makes_sense

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )
        parser.add_argument(
            "-m", "--mode", choices=["near", "prev", "next"], default="near"
        )

    async def run(self):
        if self.args.mode == "near":
            func = self.api.media.video.align_pts_to_near_frame
        elif self.args.mode == "prev":
            func = self.api.media.video.align_pts_to_prev_frame
        elif self.args.mode == "next":
            func = self.api.media.video.align_pts_to_next_frame
        else:
            assert False

        with self.api.undo.capture():
            for sub in await self.args.target.get_subtitles():
                sub.start = func(sub.start)
                sub.end = func(sub.end)


COMMANDS = [AlignSubtitlesToVideoFramesCommand]
MENU = [
    MenuCommand(
        "Align subtitles to &video frames", "align-subs-to-video-frames"
    )
]
