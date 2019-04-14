import typing as T

import psutil
from PyQt5 import QtCore, QtWidgets

from panel.colors import Colors
from panel.widgets.chart import Chart
from panel.widgets.widget import Widget


class CpuWidget(Widget):
    delay = 0

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)
        self.percentage: T.Optional[float] = None
        self._container = QtWidgets.QWidget(main_window)
        self._chart = Chart(self._container, 100)

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._chart)

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    def _refresh_impl(self) -> None:
        if self.percentage is None:
            self.percentage = psutil.cpu_percent(interval=0.1)
        else:
            self.percentage = psutil.cpu_percent(interval=1)

    def _render_impl(self) -> None:
        assert self.percentage is not None
        self._chart.addPoint(Colors.cpu_chart_line, self.percentage)
        self._chart.setLabel(f"CPU {self.percentage:.1f}%")
        self._chart.repaint()
