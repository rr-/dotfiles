import argparse
import re

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.opt.menu import MenuCommand, SubMenu

BLACK = (16, 16, 16)
WHITE = (255, 255, 255)
DURATION = 2000


def _parse_color(text):
    match = re.match(
        "#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})", text, flags=re.I
    )
    if not match:
        raise ValueError(f'Unknown color "{text}"')
    return [int(part, 16) for part in match.groups()]


def _format_color(number, color):
    if len(color) == 4:
        red, green, blue, _alpha = color
    elif len(color) == 3:
        red, green, blue = color
    else:
        raise ValueError("Unexpected color tuple length")
    return rf"\{number}c&H{blue:02X}{green:02X}{red:02X}&"


def _format_animation(start, end, *tags):
    text = _format_ass_tags(*tags, close=False)
    return rf"\t({start:.0f},{end:.0f},{text})"


def _format_ass_tags(*tags, close=True):
    joined = "".join(str(t) for t in tags)
    if close:
        return "{" + joined + "}"
    return joined


class FadeCommand(BaseCommand):
    names = ["fade"]
    help_text = "Fades selected subtitles from or into a given color."

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        with self.api.undo.capture():
            for line in self.api.subs.selected_events:
                style = self.api.subs.styles.get_by_name(line.style)

                col1 = style.primary_color
                # col2 = style.secondary_color
                col3 = style.outline_color
                col4 = style.back_color

                if self.args.src:
                    line.text = (
                        _format_ass_tags(
                            _format_color(1, self.args.src),
                            _format_color(3, self.args.src),
                            _format_color(4, self.args.src),
                            _format_animation(
                                0,
                                self.args.duration,
                                _format_color(1, col1),
                                _format_color(3, col3),
                                _format_color(4, col4),
                            ),
                            close=True,
                        )
                        + line.text
                    )
                if self.args.dst:
                    line.text = (
                        _format_ass_tags(
                            _format_animation(
                                max(0, line.duration - self.args.duration),
                                line.duration,
                                _format_color(1, self.args.dst),
                                _format_color(3, self.args.dst),
                                _format_color(4, self.args.dst),
                            ),
                            close=True,
                        )
                        + line.text
                    )

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-d",
            "--duration",
            help="how long the fade should last",
            type=int,
            required=True,
        )
        parser.add_argument(
            "-f",
            "--from",
            dest="src",
            help="color to fade from",
            type=_parse_color,
        )
        parser.add_argument(
            "-t",
            "--to",
            dest="dst",
            help="color to fade to",
            type=_parse_color,
        )


COMMANDS = [FadeCommand]
MENU = [
    SubMenu(
        "&Fade from/to…",
        [
            MenuCommand("&Fade from black", "fade -d=2000 --from=101010"),
            MenuCommand("&Fade to black", "fade -d=2000 --to=101010"),
            MenuCommand("&Fade from white", "fade -d=2000 --from=FFFFFF"),
            MenuCommand("&Fade to white", "fade -d=2000 --to=FFFFFF"),
        ],
    )
]
