import argparse
import bisect

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand, CommandUnavailable
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import Pts
from bubblesub.fmt.ass.event import AssEvent
from bubblesub.util import ms_to_str

try:
    import numpy as np
    import cv2
except ImportError as ex:
    raise CommandUnavailable(f"{ex.name} is not installed")

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_CROP = 180
BLACK_THRESHOLD = 3
WHITE_THRESHOLD = 15
DIFF_THRESHOLD = 7


def is_black(frame: np.array) -> bool:
    return np.mean(frame) < BLACK_THRESHOLD


def is_white(frame: np.array) -> bool:
    return np.mean(frame) > WHITE_THRESHOLD


class DetectKaraokeCommand(BaseCommand):
    names = ["detect-karaoke"]
    help_text = "Detect static karaoke within selected video frames."

    @property
    def is_enabled(self):
        return (
            self.api.video.current_stream
            and self.api.video.current_stream.is_ready
        )

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--start",
            help="where the sample should start",
            type=lambda value: Pts(api, value),
            default="a.s",
        )
        parser.add_argument(
            "--end",
            help="where the sample should end",
            type=lambda value: Pts(api, value),
            default="a.e",
        )

    async def run(self):
        start = await self.args.start.get()
        end = await self.args.end.get()
        if end < start:
            end, start = start, end
        if start == end:
            raise CommandUnavailable("nothing to sample")

        with self.api.undo.capture():
            start_frame_idx = self.api.video.current_stream.frame_idx_from_pts(
                start
            )
            end_frame_idx = self.api.video.current_stream.frame_idx_from_pts(
                end
            )

            sub_start = 0
            frame = self.get_frame(start_frame_idx)

            for frame_idx in range(start_frame_idx + 1, end_frame_idx):
                prev_frame = frame
                frame = self.get_frame(frame_idx).copy()

                if is_black(prev_frame) and is_white(frame):
                    start = self.api.video.current_stream.timecodes[frame_idx]

                elif is_white(prev_frame) and is_black(frame):
                    if not start:
                        continue
                    end = self.api.video.current_stream.timecodes[frame_idx]
                    self.add_sub(start, end)
                    start = 0

                elif (
                    start
                    and np.abs(np.mean(prev_frame - frame)) > DIFF_THRESHOLD
                ):
                    end = self.api.video.current_stream.timecodes[frame_idx]
                    self.add_sub(start, end)
                    start = end

    def add_sub(self, start: int, end: int) -> None:
        self.api.log.info(
            f"Detected karaoke at {ms_to_str(start)}..{ms_to_str(end)}"
        )

        idx = (
            bisect.bisect_left(
                [event.start for event in self.api.subs.events], start
            )
            if self.api.subs.events
            else 0
        )

        self.api.subs.events.insert(
            idx,
            AssEvent(
                start=start,
                end=end,
                note="detected karaoke",
                style=self.api.subs.default_style_name,
            ),
        )

    def get_frame(self, frame_idx: int) -> np.array:
        frame = self.api.video.current_stream.get_frame(
            frame_idx, FRAME_WIDTH, FRAME_HEIGHT
        )

        # crop lower part
        frame = frame[FRAME_CROP:FRAME_HEIGHT, :, :]

        # threshold the pixels
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
        kernel = kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        img = cv2.dilate(img, kernel, 1)
        img = cv2.erode(img, kernel, 2)
        img = cv2.dilate(img, kernel, 1)

        # test :)
        # cv2.imwrite(f'/tmp/test-{frame_idx}.png', img)

        return img.astype(np.int)


COMMANDS = [DetectKaraokeCommand]
MENU = [MenuCommand("&Detect karaoke", "detect-karaoke")]
