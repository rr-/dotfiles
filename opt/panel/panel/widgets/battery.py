import glob
import typing as T
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from panel.widgets.widget import Widget


def glob_path(pattern: str) -> T.Optional[Path]:
    try:
        return Path(glob.glob(pattern)[0])
    except IndexError:
        return None


class BatteryWidget(Widget):
    delay = 3

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)
        self.percentage = 0.0
        self._container = QtWidgets.QWidget(main_window)
        self._icon_label = QtWidgets.QLabel(self._container)
        self._text_label = QtWidgets.QLabel(self._container)

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)

        self._text_label.setFixedWidth(50)
        self._text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self._set_icon(self._icon_label, "battery")

        self._charge_now_path = glob_path(
            "/sys/class/power_supply/*/energy_now"
        )
        self._charge_max_path = glob_path(
            "/sys/class/power_supply/*/energy_full"
        )

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    @property
    def available(self) -> bool:
        return (
            self._charge_now_path is not None
            and self._charge_max_path is not None
        )

    def _refresh_impl(self) -> None:
        assert self._charge_now_path
        assert self._charge_max_path
        current_value = int(self._charge_now_path.read_text())
        max_value = int(self._charge_max_path.read_text())
        self.percentage = current_value * 100.0 / max_value

    def _render_impl(self) -> None:
        self._text_label.setText("%5.02f%%" % self.percentage)
