import os
import glob
from PyQt5 import QtCore, QtWidgets
from widgets.chart import Chart
from widgets.widget import Widget


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read().strip()


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
        self._net_out_icon_label = QtWidgets.QLabel()
        self._net_out_text_label = QtWidgets.QLabel()
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
            self._net_in_text_label.setText(
                '%04.0f KB/s' % (self.net_in / 1024.0))
            self._net_out_text_label.setText(
                '%04.0f KB/s' % (self.net_out / 1024.0))
            self._chart.addPoint('#0b0', self.net_in)
            self._chart.addPoint('#f00', self.net_out)
            self._chart.repaint()
