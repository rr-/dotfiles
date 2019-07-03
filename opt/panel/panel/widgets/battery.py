from PyQt5 import QtCore, QtWidgets

from panel.updaters.battery import BatteryUpdater
from panel.util import set_icon


class BatteryWidget(QtWidgets.QWidget):
    def __init__(
        self, updater: BatteryUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._updater = updater

        self._icon_label = QtWidgets.QLabel(self)
        self._text_label = QtWidgets.QLabel(self)

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)

        self._text_label.setFixedWidth(50)
        self._text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        set_icon(self._icon_label, "battery")

        self._updater.updated.connect(self._on_update)
        self._on_update(self._updater.percentage)

    def _on_update(self, percentage: float) -> None:
        self._text_label.setText(f"{percentage:.1f}%")
