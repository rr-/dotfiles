import argparse

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection


class AlignSubtitlesToVideoFramesCommand(BaseCommand):
    names = ["align-subs-to-video-frames"]
    help_text = "Aligns subtitles to video frames."

    @property
    def is_enabled(self):
        return self.api.playback.is_ready and self.args.target.makes_sense

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
            func = self.api.video.align_pts_to_near_frame
        elif self.args.mode == "prev":
            func = self.api.video.align_pts_to_prev_frame
        elif self.args.mode == "next":
            func = self.api.video.align_pts_to_next_frame
        else:
            assert False

        changed = 0
        unchanged = 0

        with self.api.undo.capture():
            for sub in await self.args.target.get_subtitles():
                new_start = func(sub.start)
                new_end = func(sub.end)

                if new_start != sub.start or new_end != sub.end:
                    sub.start = new_start
                    sub.end = new_end
                    changed += 1
                else:
                    unchanged += 1

        self.api.log.info(f"{changed} changed, {unchanged} unchanged")


COMMANDS = [AlignSubtitlesToVideoFramesCommand]
MENU = [
    MenuCommand(
        "Align subtitles to &video frames", "align-subs-to-video-frames"
    )
]
