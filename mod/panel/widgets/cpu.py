import psutil
from PyQt5 import QtCore, QtWidgets
from widgets.chart import Chart
from widgets.widget import Widget


class CpuWidget(Widget):
    delay = 0

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.percentage = None
        self._icon_label = QtWidgets.QLabel()
        self._text_label = QtWidgets.QLabel()
        self._chart = Chart(QtCore.QSize(80, main_window.height()))

        self.set_icon(self._icon_label, 'chip')

        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=6))
        container.layout().addWidget(self._icon_label)
        container.layout().addWidget(self._text_label)
        container.layout().addWidget(self._chart)
        main_window[0].layout().addWidget(container)

    def refresh_impl(self):
        if self.percentage is None:
            self.percentage = psutil.cpu_percent(interval=0.1)
        else:
            self.percentage = psutil.cpu_percent(interval=1)

    def render_impl(self):
        self._text_label.setText('%05.1f%%' % (self.percentage))
        self._chart.addPoint('#f00', self.percentage)
        self._chart.repaint()
