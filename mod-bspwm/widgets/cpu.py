import psutil
from PyQt4 import QtGui
from PyQt4 import QtCore

from .chart import Chart

class CpuProvider(object):
    delay = 0

    def __init__(self, main_window):
        self.label = QtGui.QLabel()
        self.chart = Chart(QtCore.QSize(80, main_window.height()))
        main_window[0].right_widget.layout().addWidget(self.label)
        main_window[0].right_widget.layout().addWidget(self.chart)

    def refresh(self):
        self.percentage = psutil.cpu_percent(interval=1)

    def render(self):
        self.label.setText('CPU %.1f%%' % (self.percentage))
        self.chart.addPoint('#ff0000', self.percentage)
        self.chart.repaint()