import re
from bubblesub.api.cmd import PluginCommand


class FadeFromBlackCommand(PluginCommand):
    name = 'grid/fade-from-black'
    menu_name = 'Fade from black'

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
            line.text = (
                '{'
                r'\1c&H101010&'
                r'\3c&H101010&'
                r'\t(0,2000,'
                rf'\1c&H{c1[2]:02X}{c1[1]:02X}{c1[0]:02X}'
                rf'\3c&H{c3[2]:02X}{c3[1]:02X}{c3[0]:02X}'
                '}'
            ) + line.text
