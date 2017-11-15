import glob
from PyQt5 import QtCore, QtWidgets
from panel.widgets.widget import Widget


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read().strip()


class BatteryWidget(Widget):
    delay = 3

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.percentage = None
        self._container = QtWidgets.QWidget(main_window)
        self._icon_label = QtWidgets.QLabel(self._container)
        self._text_label = QtWidgets.QLabel(self._container)

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)

        self._text_label.setFixedWidth(50)
        self._text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self._set_icon(self._icon_label, 'battery')

        try:
            self._charge_now_path = glob.glob(
                '/sys/class/power_supply/*/energy_now')[0]
            self._charge_max_path = glob.glob(
                '/sys/class/power_supply/*/energy_full')[0]
        except IndexError:
            self._charge_now_path = None
            self._charge_max_path = None

    @property
    def container(self):
        return self._container

    @property
    def available(self):
        return self._charge_now_path and self._charge_max_path

    def _refresh_impl(self):
        current_value = int(read_file(self._charge_now_path))
        max_value = int(read_file(self._charge_max_path))
        self.percentage = current_value * 100.0 / max_value

    def _render_impl(self):
        self._text_label.setText('%5.02f%%' % self.percentage)
