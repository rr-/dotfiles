from PyQt5 import QtWidgets

from panel.widgets.base import BaseWidget


class StretchWidget(BaseWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setProperty("class", "stretch")
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
