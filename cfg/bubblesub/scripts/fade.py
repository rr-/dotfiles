import re
from enum import Enum
import bubblesub.util
from bubblesub.api.cmd import PluginCommand


BLACK = (16, 16, 16)
WHITE = (255, 255, 255)
DURATION = 2000


class Direction(Enum):
    Left = -1
    Right = 1


def format_color(number, color):
    if len(color) == 4:
        red, green, blue, _alpha = color
    elif len(color) == 3:
        red, green, blue = color
    else:
        raise ValueError('Unexpected color tuple length')
    return rf'\{number}c&H{blue:02X}{green:02X}{red:02X}&'


def format_animation(start, end, *tags):
    text = format_ass_tags(*tags, close=False)
    return rf'\t({start:.0f},{end:.0f},{text})'


def format_ass_tags(*tags, close=True):
    joined = ''.join(str(t) for t in tags)
    if close:
        return '{' + joined + '}'
    return joined


class FadeCommand:
    @bubblesub.util.classproperty
    def name(self):
        ret = 'grid/fade-'
        ret += str(self.direction) + '-'
        ret += str(self.color)
        return ret

    @bubblesub.util.classproperty
    def duration(self):
        raise NotImplementedError('Unknown duration')

    @bubblesub.util.classproperty
    def direction(self):
        raise NotImplementedError('Unknown direction')

    @bubblesub.util.classproperty
    def color(self):
        raise NotImplementedError('Unknown color')

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            style = self.api.subs.styles.get_by_name(line.style)
            c1 = style.primary_color
            c2 = style.secondary_color
            c3 = style.outline_color
            c4 = style.back_color

            if self.direction == Direction.Left:
                line.text = format_ass_tags(
                    format_color(1, self.color),
                    format_color(3, self.color),
                    format_color(4, self.color),
                    format_animation(
                        0,
                        self.duration,
                        format_color(1, c1),
                        format_color(3, c3),
                        format_color(4, c4)),
                    close=True) + line.text
            elif self.direction == Direction.Right:
                line.text = format_ass_tags(
                    format_animation(
                        max(0, line.duration - self.duration),
                        line.duration,
                        format_color(1, self.color),
                        format_color(3, self.color),
                        format_color(4, self.color)),
                    close=True) + line.text
            else:
                raise ValueError('Invalid direction')


def define_cmd(menu_name, color, direction):
    type(
        'CustomFadeCommand',
        (FadeCommand, PluginCommand),
        {
            'direction': direction,
            'color': color,
            'menu_name': menu_name,
            'duration': DURATION,
        })


for menu_name, color, direction in [
        ('Fade from &black', BLACK, Direction.Left),
        ('Fade from &white', WHITE, Direction.Left),
        ('Fade to &black', BLACK, Direction.Right),
        ('Fade to &white', WHITE, Direction.Right)]:
    define_cmd(menu_name, color, direction)
