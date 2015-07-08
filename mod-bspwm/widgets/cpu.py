import psutil
from PyQt4 import QtGui

class CpuProvider(object):
    delay = 0

    def __init__(self, main_window):
        self.label = QtGui.QLabel()
        main_window[0].right_widget.layout().addWidget(self.label)

    def refresh(self):
        self.percentage = psutil.cpu_percent(interval=1)

    def render(self):
        self.label.setText('CPU: %5.02f%%' % (self.percentage))

