from PyQt4 import QtGui
import glob

def read_file(path):
    with open(path, 'r') as fh:
        return fh.read().strip()

class BatteryProvider(object):
    delay = 3

    def __init__(self, main_window):
        try:
            self.charge_now = glob.glob('/sys/class/power_supply/*/charge_now')[0]
            self.charge_max = glob.glob('/sys/class/power_supply/*/charge_full')[0]
            self.charge_status = glob.glob('/sys/class/power_supply/*/status')[0]
            self.battery_present = True
            self.label = QtGui.QLabel()
            main_window[0].right_widget.layout().addWidget(self.label)
        except IndexError:
            self.battery_present = False

    def refresh(self):
        if self.battery_present:
            now = int(read_file(self.charge_now))
            max = int(read_file(self.charge_max))
            self.status = read_file(self.charge_status).lower()
            self.percentage = now * 100.0 / max
            time.sleep(3)

    def render(self):
        if self.battery_present:
            self.label.setText('Battery: %5.02f%% (%s)', self.percentage, self.status)
