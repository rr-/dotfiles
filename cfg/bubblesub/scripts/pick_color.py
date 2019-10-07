import typing as T

from PyQt5 import QtWidgets
from pyqtcolordialog import QColorDialog

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand


class PickColorCommand(BaseCommand):
    names = ["pick-color"]
    help_text = "Runs a color dialog and prints ASS tags for it."

    async def run(self) -> None:
        await self.api.gui.exec(self._run_with_gui)

    async def _run_with_gui(self, main_window: QtWidgets.QMainWindow) -> None:
        color = QColorDialog.getColor(None, main_window)
        if color.isValid():
            self.api.log.info(
                f"RGB: #"
                f"{color.red():02X}"
                f"{color.green():02X}"
                f"{color.blue():02X}"
                f" ASS: \\c&H"
                f"{color.blue():02X}"
                f"{color.green():02X}"
                f"{color.red():02X}"
                f"&"
            )


COMMANDS = [PickColorCommand]
MENU = [MenuCommand("&Pick color", "pick-color")]
