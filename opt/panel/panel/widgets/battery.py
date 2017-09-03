import glob
from PyQt5 import QtWidgets
from panel.widgets.widget import Widget


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read().strip()


class BatteryWidget(Widget):
    delay = 3

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.percentage = None

        try:
            self._charge_now_path = glob.glob(
                '/sys/class/power_supply/*/energy_now')[0]
            self._charge_max_path = glob.glob(
                '/sys/class/power_supply/*/energy_full')[0]
        except IndexError:
            self._charge_now_path = None
            self._charge_max_path = None

        self._label = QtWidgets.QLabel(main_window)

    @property
    def container(self):
        return self._label

    @property
    def available(self):
        return self._charge_now_path and self._charge_max_path

    def _refresh_impl(self):
        current_value = int(read_file(self._charge_now_path))
        max_value = int(read_file(self._charge_max_path))
        self.percentage = current_value * 100.0 / max_value

    def _render_impl(self):
        self._label.setText('Battery: %5.02f%%' % self.percentage)
