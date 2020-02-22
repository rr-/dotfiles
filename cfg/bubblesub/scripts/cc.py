import re

from PyQt5 import QtWidgets

from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand
from bubblesub.fmt.ass.event import AssEvent
from bubblesub.ui.util import load_dialog

try:
    import pysubs2
except ImportError as ex:
    raise CommandUnavailable(f"{ex.name} is not installed")


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
                    AssEvent(
                        start=line.start,
                        end=line.end,
                        note=line.text,
                        style=self.api.subs.default_style_name,
                    )
                )


COMMANDS = [LoadClosedCaptionsCommand]
MENU = [MenuCommand("&Load closed captions", "load-cc")]
