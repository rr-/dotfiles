from enum import Enum

from bubblesub.opt.menu import SubMenu
from bubblesub.opt.menu import MenuCommand
from bubblesub.api.cmd import BaseCommand


BLACK = (16, 16, 16)
WHITE = (255, 255, 255)
DURATION = 2000


class _Direction(Enum):
    Left = -1
    Right = 1


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
    name = 'plugin/fade'

    def __init__(
            self,
            api,
            duration: int,
            direction: _Direction,
            color: str
    ) -> None:
        super().__init__(api)
        self._duration = duration
        self._direction = direction
        self._color = color

    @property
    def menu_name(self):
        ret = '&Fade '
        if self._direction == _Direction.Left:
            ret += 'from '
        else:
            ret += 'to '
        ret += '#' + ''.join(f'{comp:02X}' for comp in self._color)
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

                if self._direction == _Direction.Left:
                    line.text = _format_ass_tags(
                        _format_color(1, self._color),
                        _format_color(3, self._color),
                        _format_color(4, self._color),
                        _format_animation(
                            0,
                            self._duration,
                            _format_color(1, col1),
                            _format_color(3, col3),
                            _format_color(4, col4)
                        ),
                        close=True
                    ) + line.text
                elif self._direction == _Direction.Right:
                    line.text = _format_ass_tags(
                        _format_animation(
                            max(0, line.duration - self._duration),
                            line.duration,
                            _format_color(1, self._color),
                            _format_color(3, self._color),
                            _format_color(4, self._color)
                        ),
                        close=True
                    ) + line.text
                else:
                    raise ValueError('Invalid direction')


def register(cmd_api):
    cmd_api.register_plugin_command(
        FadeCommand,
        SubMenu(
            '&Fade from/to…',
            [
                MenuCommand(
                    FadeCommand.name, DURATION, _Direction.Left, BLACK
                ),
                MenuCommand(
                    FadeCommand.name, DURATION, _Direction.Left, WHITE
                ),
                MenuCommand(
                    FadeCommand.name, DURATION, _Direction.Right, BLACK
                ),
                MenuCommand(
                    FadeCommand.name, DURATION, _Direction.Right, WHITE
                )
            ]
        )
    )
