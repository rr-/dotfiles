import re
from bubblesub.api.cmd import PluginCommand


class ConvertCommentsCommand(PluginCommand):
    name = 'grid/convert-comments'
    menu_name = 'Convert old style notes'

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            match = re.search('{([^\\\\{}][^{}]*)}', line.text)
            if match:
                line.note = match.group(1)
                line.text = line.text[:match.start()] + line.text[match.end():]
