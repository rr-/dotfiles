import re
import pysubs2
import bubblesub.ui.util
from bubblesub.api.cmd import PluginCommand


class LoadClosedCaptionsCommand(PluginCommand):
    name = 'grid/load-closed-captions'
    menu_name = '&Load closed captions'

    @property
    def is_enabled(self):
        return True

    async def run(self):
        await self.api.gui.exec(self._run)

    @staticmethod
    async def _run(api, main_window):
        path = bubblesub.ui.util.load_dialog(
            main_window,
            'Subtitles (*.ass *.srt);;All files (*.*)')
        if not path:
            return

        source = pysubs2.load(str(path))
        for line in source:
            api.subs.lines.insert_one(
                len(api.subs.lines),
                start=line.start,
                end=line.end,
                note=line.text)


class CleanClosedCaptionsCommand(PluginCommand):
    name = 'grid/clean-closed-captions'
    menu_name = '&Clean closed captions'

    @property
    def is_enabled(self):
        return True

    async def run(self):
        await self.api.gui.exec(self._run)

    @staticmethod
    async def _run(api, _main_window):
        with api.undo.bulk():
            for line in api.subs.selected_lines:
                note = line.note
                note = re.sub(r'\\N', '\n', note)
                note = re.sub(r'\(\(\)\)', '', note)  # retrospection
                note = re.sub(r'\([^\(\)]*\)', '', note)  # actors
                note = re.sub(r'\[[^\[\]]*\]', '', note)  # actors
                note = re.sub('[➡→]', '', note)  # line continuation
                note = re.sub('≪', '', note)  # distant dialogues
                note = re.sub('[＜＞《》]', '', note)
                note = re.sub('｡', '。', note)  # half-width period
                note = re.sub('([…！？])。', r'\1', note)  # superfluous periods
                note = note.rstrip('・')
                note = re.sub(' ', '', note)  # Japanese doesn't need spaces
                note = note.strip()
                line.note = note
