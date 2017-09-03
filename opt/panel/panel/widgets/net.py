import os
import glob
import math
from PyQt5 import QtCore, QtWidgets
from panel.widgets.chart import Chart
from panel.widgets.widget import Widget
from panel.colors import Colors


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read().strip()


def convert_speed(speed_bytes):
    suffixes = ("B/s", "KB/s", "MB/s", "GB/s", "TB/s")
    if speed_bytes < 1024:
        return '{:.0f} {}'.format(speed_bytes, suffixes[0])
    power = int(math.floor(math.log(speed_bytes, 1024)))
    denominator = math.pow(1024, power)
    return f'{speed_bytes / denominator:.1f} {suffixes[power]}'


class NetworkUsageWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.net_in = 0
        self.net_out = 0

        try:
            self._rx_path = None
            self._tx_path = None
            for interface in glob.glob('/sys/class/net/*'):
                state = read_file(os.path.join(interface, 'operstate'))
                if state.lower() == 'up':
                    self._rx_path = os.path.join(
                        interface, 'statistics', 'rx_bytes')
                    self._tx_path = os.path.join(
                        interface, 'statistics', 'tx_bytes')
                    self._available = True
        except Exception:
            pass

        if self._available:
            self._old_rx_bytes = int(read_file(self._rx_path))
            self._old_tx_bytes = int(read_file(self._tx_path))
        else:
            self._old_rx_bytes = None
            self._old_tx_bytes = None

        self._container = QtWidgets.QWidget(main_window)
        self._net_in_icon_label = QtWidgets.QLabel(self._container)
        self._net_in_text_label = QtWidgets.QLabel(self._container)
        self._net_out_icon_label = QtWidgets.QLabel(self._container)
        self._net_out_text_label = QtWidgets.QLabel(self._container)
        self._chart = Chart(self._container, 80)

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._net_in_icon_label)
        layout.addWidget(self._net_in_text_label)
        layout.addWidget(self._net_out_icon_label)
        layout.addWidget(self._net_out_text_label)
        layout.addWidget(self._chart)

        self._set_icon(self._net_in_icon_label, 'arrow-down')
        self._set_icon(self._net_out_icon_label, 'arrow-up')
        self._net_in_text_label.setFixedWidth(65)
        self._net_in_text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self._net_out_text_label.setFixedWidth(65)
        self._net_out_text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    @property
    def container(self):
        return self._container

    @property
    def available(self):
        return self._rx_path and self._tx_path

    def _refresh_impl(self):
        rx_bytes = int(read_file(self._rx_path))
        tx_bytes = int(read_file(self._tx_path))
        self.net_in = (rx_bytes - self._old_rx_bytes) / 1
        self.net_out = (tx_bytes - self._old_tx_bytes) / 1
        self._old_rx_bytes = rx_bytes
        self._old_tx_bytes = tx_bytes

    def _render_impl(self):
        self._net_in_text_label.setText(convert_speed(self.net_in))
        self._net_out_text_label.setText(convert_speed(self.net_out))
        self._chart.addPoint(Colors.net_up_chart_line, self.net_in)
        self._chart.addPoint(Colors.net_down_chart_line, self.net_out)
        self._chart.update()
