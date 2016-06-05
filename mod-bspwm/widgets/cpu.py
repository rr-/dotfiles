import psutil
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from widgets.chart import Chart

class CpuProvider(object):
    delay = 0

    def __init__(self, main_window):
        self.percentage = None
        self._label = QtWidgets.QLabel()
        self._chart = Chart(QtCore.QSize(80, main_window.height()))
        main_window[0].right_widget.layout().addWidget(self._label)
        main_window[0].right_widget.layout().addWidget(self._chart)

    def refresh(self):
        self.percentage = psutil.cpu_percent(interval=1)

    def render(self):
        self._label.setText('CPU %05.1f%%' % (self.percentage))
        self._chart.addPoint('#f00', self.percentage)
        self._chart.repaint()
