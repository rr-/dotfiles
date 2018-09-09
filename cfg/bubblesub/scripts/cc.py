import re

import pysubs2
import bubblesub.api.cmd
import bubblesub.ui.util


class LoadClosedCaptionsCommand(bubblesub.api.cmd.BaseCommand):
    names = ['load-cc']
    help_text = 'Loads closed captions from a file.'

    async def run(self):
        await self.api.gui.exec(self._run)

    async def _run(self, _api, main_window):
        path = bubblesub.ui.util.load_dialog(
            main_window, 'Subtitles (*.ass *.srt);;All files (*.*)'
        )
        if not path:
            return

        source = pysubs2.load(str(path))
        with self.api.undo.capture():
            for line in source:
                self.api.subs.events.insert_one(
                    len(self.api.subs.events),
                    start=line.start,
                    end=line.end,
                    note=line.text
                )


class CleanClosedCaptionsCommand(bubblesub.api.cmd.BaseCommand):
    names = ['clean-cc']
    help_text = (
        'Cleans common closed caption punctuation from the selected events.'
    )

    async def run(self):
        with self.api.undo.capture():
            for line in api.subs.selected_events:
                note = line.note
                note = re.sub(r'\\N', '\n', note)
                note = re.sub(r'\(\(\)\)', '', note)  # retrospection
                note = re.sub(r'\([^\(\)]*\)', '', note)  # actors
                note = re.sub(r'\[[^\[\]]*\]', '', note)  # actors
                note = re.sub('[➡→]', '', note)  # line continuation
                note = re.sub('≪', '', note)  # distant dialogues
                note = re.sub('[＜＞《》]', '', note)
                note = re.sub('｡', '。', note)  # half-width period
                note = re.sub('([…！？])。', r'\1', note)  # unneeded periods
                note = note.rstrip('・')
                note = re.sub(' ', '', note)  # Japanese doesn't need spaces
                note = note.strip()
                line.note = note


def register(cmd_api):
    cmd_api.register_plugin_command(
        LoadClosedCaptionsCommand,
        bubblesub.opt.menu.MenuCommand('&Load closed captions', '/load-cc')
    )
    cmd_api.register_plugin_command(
        CleanClosedCaptionsCommand,
        bubblesub.opt.menu.MenuCommand('&Clean closed captions', '/clean-cc')
    )
