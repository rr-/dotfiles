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
    suffix = ("B/s", "KB/s", "MB/s", "GB/s", "TB/s")
    if speed_bytes < 1024:
        return '{:.0f} {}'.format(speed_bytes, suffix[0])
    i = int(math.floor(math.log(speed_bytes, 1024)))
    p = math.pow(1024, i)
    return '{:.1f} {}'.format(round(speed_bytes/p, 2), suffix[i])


class NetworkUsageWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.net_in = 0
        self.net_out = 0
        self.network_enabled = False
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
                    self.network_enabled = True
        except:
            pass

        if not self.network_enabled:
            return

        self._old_rx_bytes = int(read_file(self._rx_path))
        self._old_tx_bytes = int(read_file(self._tx_path))
        self._net_in_icon_label = QtWidgets.QLabel()
        self._net_in_text_label = QtWidgets.QLabel()
        self._net_in_text_label.setFixedWidth(65)
        self._net_in_text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self._net_out_icon_label = QtWidgets.QLabel()
        self._net_out_text_label = QtWidgets.QLabel()
        self._net_out_text_label.setFixedWidth(65)
        self._net_out_text_label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self._chart = Chart(QtCore.QSize(80, main_window.height()))

        self.set_icon(self._net_in_icon_label, 'arrow-down')
        self.set_icon(self._net_out_icon_label, 'arrow-up')

        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=6))
        container.layout().addWidget(self._net_in_icon_label)
        container.layout().addWidget(self._net_in_text_label)
        container.layout().addWidget(self._net_out_icon_label)
        container.layout().addWidget(self._net_out_text_label)
        container.layout().addWidget(self._chart)
        main_window[0].layout().addWidget(container)
        self._chart.repaint()

    def refresh_impl(self):
        if self.network_enabled:
            rx_bytes = int(read_file(self._rx_path))
            tx_bytes = int(read_file(self._tx_path))
            self.net_in = (rx_bytes - self._old_rx_bytes) / 1
            self.net_out = (tx_bytes - self._old_tx_bytes) / 1
            self._old_rx_bytes = rx_bytes
            self._old_tx_bytes = tx_bytes

    def render_impl(self):
        if self.network_enabled:
            self._net_in_text_label.setText(convert_speed(self.net_in))
            self._net_out_text_label.setText(convert_speed(self.net_out))
            self._chart.addPoint(Colors.net_up_chart_line, self.net_in)
            self._chart.addPoint(Colors.net_down_chart_line, self.net_out)
            self._chart.repaint()
