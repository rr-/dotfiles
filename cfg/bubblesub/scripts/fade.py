import abc
from enum import Enum

from bubblesub.model import classproperty
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


class FadeCommand(PluginCommand):
    @classproperty
    def name(cls):
        ret = 'grid/fade-'
        ret += cls.direction.name.lower() + '-'
        ret += ''.join(f'{c:02x}' for c in cls.color)
        return ret

    @abc.abstractproperty
    @classproperty
    def duration(cls):
        raise NotImplementedError('Unknown duration')

    @abc.abstractproperty
    @classproperty
    def direction(cls):
        raise NotImplementedError('Unknown direction')

    @abc.abstractproperty
    @classproperty
    def color(cls):
        raise NotImplementedError('Unknown color')

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        with self.api.undo.capture():
            for line in self.api.subs.selected_lines:
                style = self.api.subs.styles.get_by_name(line.style)

                col1 = style.primary_color
                # col2 = style.secondary_color
                col3 = style.outline_color
                col4 = style.back_color

                if self.direction == Direction.Left:
                    line.text = format_ass_tags(
                        format_color(1, self.color),
                        format_color(3, self.color),
                        format_color(4, self.color),
                        format_animation(
                            0,
                            self.duration,
                            format_color(1, col1),
                            format_color(3, col3),
                            format_color(4, col4)),
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


def define_cmds():
    for menu_name, color, direction in [
            ('Fade from &black', BLACK, Direction.Left),
            ('Fade from &white', WHITE, Direction.Left),
            ('Fade to &black', BLACK, Direction.Right),
            ('Fade to &white', WHITE, Direction.Right)]:
        define_cmd(menu_name, color, direction)


define_cmds()
