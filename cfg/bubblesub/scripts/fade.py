import argparse
import re

from bubblesub.opt.menu import SubMenu
from bubblesub.opt.menu import MenuCommand
from bubblesub.api.cmd import BaseCommand
from bubblesub.util import HorizontalDirection


BLACK = (16, 16, 16)
WHITE = (255, 255, 255)
DURATION = 2000


def _parse_color(text):
    match = re.match(
        '#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})',
        text,
        flags=re.I
    )
    if not match:
        raise ValueError(f'Unknown color "{text}"')
    return [
        int(part, 16)
        for part in match.groups()
    ]


def _format_color(number, color):
    if len(color) == 4:
        red, green, blue, _alpha = color
    elif len(color) == 3:
        red, green, blue = color
    else:
        raise ValueError('Unexpected color tuple length')
    return rf'\{number}c&H{blue:02X}{green:02X}{red:02X}&'


def _format_animation(start, end, *tags):
    text = _format_ass_tags(*tags, close=False)
    return rf'\t({start:.0f},{end:.0f},{text})'


def _format_ass_tags(*tags, close=True):
    joined = ''.join(str(t) for t in tags)
    if close:
        return '{' + joined + '}'
    return joined


class FadeCommand(BaseCommand):
    name = 'fade'
    help_text = 'Fades selected subtitles from or into a given color.'

    @property
    def menu_name(self):
        ret = '&Fade '
        if self.args.direction == HorizontalDirection.Left:
            ret += 'from '
        else:
            ret += 'to '
        ret += '#' + ''.join(f'{comp:02X}' for comp in self.args.color)
        return ret

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

                if self.args.direction == HorizontalDirection.Left:
                    line.text = _format_ass_tags(
                        _format_color(1, self.args.color),
                        _format_color(3, self.args.color),
                        _format_color(4, self.args.color),
                        _format_animation(
                            0,
                            self.args.duration,
                            _format_color(1, col1),
                            _format_color(3, col3),
                            _format_color(4, col4)
                        ),
                        close=True
                    ) + line.text
                elif self.args.direction == HorizontalDirection.Right:
                    line.text = _format_ass_tags(
                        _format_animation(
                            max(0, line.duration - self.args.duration),
                            line.duration,
                            _format_color(1, self.args.color),
                            _format_color(3, self.args.color),
                            _format_color(4, self.args.color)
                        ),
                        close=True
                    ) + line.text
                else:
                    raise ValueError('Invalid direction')

    @staticmethod
    def _decorate_parser(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-d', '--duration',
            help='how long the fade should last',
            type=int,
            required=True
        )
        parser.add_argument(
            '--direction',
            help='how to fade the subtitle',
            type=HorizontalDirection.from_string,
            choices=list(HorizontalDirection),
            required=True
        )
        parser.add_argument(
            '-c', '--color',
            help='how to insert the subtitle',
            type=_parse_color,
            required=True
        )


def register(cmd_api):
    cmd_api.register_plugin_command(
        FadeCommand,
        SubMenu(
            '&Fade from/to…',
            [
                MenuCommand('/fade -d 2000 --direction left -c #101010'),
                MenuCommand('/fade -d 2000 --direction right -c #101010'),
                MenuCommand('/fade -d 2000 --direction left -c #FFFFFF'),
                MenuCommand('/fade -d 2000 --direction right -c #FFFFFF'),
            ]
        )
    )
