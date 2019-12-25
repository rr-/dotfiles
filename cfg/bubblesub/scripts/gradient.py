import argparse
import re
import typing as T
from copy import copy
from dataclasses import dataclass

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand, CommandUnavailable
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection

RGB_REGEX = re.compile(
    r"^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$", flags=re.I
)
ASS_COLOR_REGEX = re.compile(
    r"\\1?c&H([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})&", flags=re.I
)


@dataclass
class Color:
    r: int
    g: int
    b: int


@dataclass
class Transform:
    x1: float
    x2: float
    y1: float
    y2: float
    c: Color


def get_transform(
    api: Api,
    y1: int,
    y2: int,
    c1: Color,
    c2: Color,
    step: float,
    next_step: float,
) -> Transform:
    return Transform(
        x1=0,
        y1=y1 + step * (y2 - y1),
        x2=api.video.current_frame.width,
        y2=y1 + next_step * (y2 - y1),
        c=Color(
            int(c1.r + step * (c2.r - c1.r)),
            int(c1.g + step * (c2.g - c1.g)),
            int(c1.b + step * (c2.b - c1.b)),
        ),
    )


def rgb(text: str) -> Color:
    match = RGB_REGEX.match(text)
    if not match:
        raise ValueError(f'"{text}" is not a valid color')
    return Color(
        r=int(match.group(1), 16),
        g=int(match.group(2), 16),
        b=int(match.group(3), 16),
    )


class GradientCommand(BaseCommand):
    names = ["gradient"]
    help_text = (
        "Emulates a gradient effect through alternating fill colors "
        "in clip paths."
    )

    @property
    def is_enabled(self) -> bool:
        return self.args.target.makes_sense

    async def run(self) -> None:
        events = await self.args.target.get_subtitles()

        if len(events) != 1:
            raise CommandUnavailable("too many subtitles selected")

        with self.api.undo.capture():
            event = events[0]

            if not self.args.only_print:
                event.is_comment = True

            for i in range(self.args.steps):
                step = i / (self.args.steps - 1)
                next_step = (i + 1) / (self.args.steps - 1)

                t = get_transform(
                    self.api,
                    self.args.y1,
                    self.args.y2,
                    self.args.c1,
                    self.args.c2,
                    step,
                    next_step,
                )

                prefix = (
                    f"{{"
                    f"\\clip({t.x1:.02f},{t.y1:.02f},{t.x2:.02f},{t.y2:.02f})"
                    f"\\1c&H{t.c.b:02X}{t.c.g:02X}{t.c.r:02X}&"
                    f"}}"
                )

                new_event = copy(event)
                new_event.text = prefix + ASS_COLOR_REGEX.sub(
                    "", new_event.text
                )
                new_event.is_comment = False

                if self.args.only_print:
                    self.api.log.info(prefix)
                else:
                    self.api.subs.events.insert(event.index + 1 + i, new_event)

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
            "-y1",
            help="Starting position of the gradient",
            type=float,
            required=True,
        )
        parser.add_argument(
            "-y2",
            help="Ending position of the gradient",
            type=float,
            required=True,
        )
        parser.add_argument(
            "-c1", help="Source color", type=rgb, required=True
        )
        parser.add_argument(
            "-c2", help="Target color", type=rgb, required=True
        )
        parser.add_argument(
            "--steps", help="How many steps to use", type=int, default=20
        )
        parser.add_argument("--only-print", action="store_true")


COMMANDS = [GradientCommand]
MENU = []
