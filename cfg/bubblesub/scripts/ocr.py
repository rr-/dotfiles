import argparse
import bisect

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand, CommandUnavailable
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import Pts, SubtitlesSelection
from bubblesub.util import ms_to_str

try:
    import cv2
    import numpy as np
    import pytesseract
except ImportError as ex:
    raise CommandUnavailable("numpy is not installed")

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


class OCRCommand(BaseCommand):
    names = ["ocr"]
    help_text = "Perform optical recognition on given frame."

    @property
    def is_enabled(self):
        return self.api.video.is_ready and self.args.target.makes_sense

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--pts",
            help="which frame to sample",
            type=lambda value: Pts(api, value),
            default="cf",
        )
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )
        parser.add_argument(
            "-l",
            "--lang",
            "--language",
            help="language used for detection",
            default="jpn",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            help="threshold to filter the character data",
            default=230,
        )

    async def run(self):
        pts = await self.args.pts.get()

        frame_idx = self.api.video.frame_idx_from_pts(pts)
        text = self.ocr_frame(frame_idx)

        with self.api.undo.capture():
            for event in await self.args.target.get_subtitles():
                event.note = text

    def ocr_frame(self, frame_idx: int) -> str:
        frame = self.api.video.get_frame(frame_idx, FRAME_WIDTH, FRAME_HEIGHT)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(
            img, self.args.threshold, 255, cv2.THRESH_BINARY
        )

        ret = pytesseract.image_to_string(img, self.args.lang)
        if self.args.lang in {"jpn"}:
            ret = ret.replace(" ", "")
        return ret


COMMANDS = [OCRCommand]
MENU = [MenuCommand("&OCR", "ocr")]
