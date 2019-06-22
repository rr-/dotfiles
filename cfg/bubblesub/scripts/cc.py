import re

import pysubs2
from PyQt5 import QtWidgets

from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.fmt.ass.event import AssEvent
from bubblesub.ui.util import load_dialog


class LoadClosedCaptionsCommand(BaseCommand):
    names = ["load-cc"]
    help_text = "Loads closed captions from a file."

    async def run(self):
        await self.api.gui.exec(self._run)

    async def _run(self, main_window: QtWidgets.QMainWindow) -> None:
        path = load_dialog(
            main_window, "Subtitles (*.ass *.srt);;All files (*.*)"
        )
        if not path:
            return

        source = pysubs2.load(str(path))
        with self.api.undo.capture():
            for line in source:
                self.api.subs.events.append(
                    AssEvent(start=line.start, end=line.end, note=line.text)
                )


class CleanClosedCaptionsCommand(BaseCommand):
    names = ["clean-cc"]
    help_text = (
        "Cleans common closed caption punctuation from the selected events."
    )

    async def run(self):
        with self.api.undo.capture():
            for line in self.api.subs.selected_events:
                note = line.note
                note = re.sub(r"\\N", "\n", note)
                note = re.sub(r"\(\(\)\)", "", note)  # retrospection
                note = re.sub(r"\([^\(\)]*\)", "", note)  # actors
                note = re.sub(r"\[[^\[\]]*\]", "", note)  # actors
                note = re.sub("[➡→]", "", note)  # line continuation
                note = re.sub("≪", "", note)  # distant dialogues
                note = re.sub("[＜＞《》]", "", note)
                note = re.sub("｡", "。", note)  # half-width period
                note = re.sub("([…！？])。", r"\1", note)  # unneeded periods
                note = note.rstrip("・")
                note = re.sub(" ", "", note)  # Japanese doesn't need spaces
                note = note.strip()
                line.note = note


COMMANDS = [LoadClosedCaptionsCommand, CleanClosedCaptionsCommand]
MENU = [
    MenuCommand("&Load closed captions", "load-cc"),
    MenuCommand("&Clean closed captions", "clean-cc"),
]
