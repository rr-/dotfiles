import psutil
from PyQt5 import QtCore, QtWidgets
from widgets.chart import Chart


class CpuWidget:
    delay = 0

    def __init__(self, main_window):
        self.percentage = None
        self._label = QtWidgets.QLabel()
        self._chart = Chart(QtCore.QSize(80, main_window.height()))

        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=8))
        container.layout().addWidget(self._label)
        container.layout().addWidget(self._chart)
        main_window[0].layout().addWidget(container)

    def refresh(self):
        if self.percentage is None:
            self.percentage = psutil.cpu_percent(interval=0.1)
        else:
            self.percentage = psutil.cpu_percent(interval=1)

    def render(self):
        self._label.setText('CPU %05.1f%%' % (self.percentage))
        self._chart.addPoint('#f00', self.percentage)
        self._chart.repaint()
