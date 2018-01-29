import re
from bubblesub.api.cmd import PluginCommand


BLACK = (16, 16, 16)
DURATION = 2000


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


class FadeFromBlackCommand(PluginCommand):
    name = 'grid/fade-from-black'
    menu_name = '&Fade from black'

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
            line.text = format_ass_tags(
                format_color(1, BLACK),
                format_color(3, BLACK),
                format_animation(
                    0,
                    DURATION,
                    format_color(1, c1),
                    format_color(3, c3)),
                close=True) + line.text


class FadeToBlackCommand(PluginCommand):
    name = 'grid/fade-to-black'
    menu_name = '&Fade to black'

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
            line.text = format_ass_tags(
                format_color(1, c1),
                format_color(3, c3),
                format_animation(
                    max(0, line.duration - DURATION),
                    line.duration,
                    format_color(1, BLACK),
                    format_color(3, BLACK)),
                close=True) + line.text
