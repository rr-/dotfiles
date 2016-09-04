import os
import glob
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from widgets.chart import Chart


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read().strip()


class NetworkUsageProvider(object):
    delay = 1

    def __init__(self, main_window):
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

        if self.network_enabled:
            self._old_rx_bytes = int(read_file(self._rx_path))
            self._old_tx_bytes = int(read_file(self._tx_path))
            self._net_in_label = QtWidgets.QLabel()
            self._net_out_label = QtWidgets.QLabel()
            self._chart = Chart(QtCore.QSize(80, main_window.height()))
            for w in [self._net_in_label, self._net_out_label, self._chart]:
                main_window[0].right_widget.layout().addWidget(w)
            self._chart.repaint()

    def refresh(self):
        if self.network_enabled:
            rx_bytes = int(read_file(self._rx_path))
            tx_bytes = int(read_file(self._tx_path))
            self.net_in = (rx_bytes - self._old_rx_bytes) / 1
            self.net_out = (tx_bytes - self._old_tx_bytes) / 1
            self._old_rx_bytes = rx_bytes
            self._old_tx_bytes = tx_bytes

    def render(self):
        if self.network_enabled:
            self._net_in_label.setText(
                '\U0001f847 %03.0f KB/s' % (self.net_in / 1024.0))
            self._net_out_label.setText(
                '\U0001f845 %03.0f KB/s' % (self.net_out / 1024.0))
            self._chart.addPoint('#0b0', self.net_in)
            self._chart.addPoint('#f00', self.net_out)
            self._chart.repaint()
