from PyQt4 import QtGui
import os
import glob

def read_file(path):
    with open(path, 'r') as fh:
        return fh.read().strip()

class NetworkUsageProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.network_enabled = False
        try:
            self.rx_path = None
            self.tx_path = None
            for interface in glob.glob('/sys/class/net/*'):
                state = read_file(os.path.join(interface, 'operstate'))
                if state.lower() == 'up':
                    self.rx_path = os.path.join(interface, 'statistics', 'rx_bytes')
                    self.tx_path = os.path.join(interface, 'statistics', 'tx_bytes')
                    self.network_enabled = True
        except:
            pass

        if self.network_enabled:
            self.old_rx_bytes = int(read_file(self.rx_path))
            self.old_tx_bytes = int(read_file(self.tx_path))
            self.net_in_label = QtGui.QLabel()
            self.net_out_label = QtGui.QLabel()
            for w in [self.net_in_label, self.net_out_label]:
                main_window[0].right_widget.layout().addWidget(w)

    def refresh(self):
        if self.network_enabled:
            rx_bytes = int(read_file(self.rx_path))
            tx_bytes = int(read_file(self.tx_path))
            self.net_in = (rx_bytes - self.old_rx_bytes) / 1
            self.net_out = (tx_bytes - self.old_tx_bytes) / 1
            self.old_rx_bytes = rx_bytes
            self.old_tx_bytes = tx_bytes

    def render(self):
        if self.network_enabled:
            self.net_in_label.setText('DL: %5.02f KB/s' % (self.net_in / 1024.0))
            self.net_out_label.setText('UL: %5.02f KB/s' % (self.net_out / 1024.0))
