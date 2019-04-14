import typing as T

import psutil
from PyQt5 import QtCore, QtWidgets

from panel.colors import Colors
from panel.widgets.chart import Chart
from panel.widgets.widget import Widget


class MemoryWidget(Widget):
    delay = 1

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
        self.percentage = psutil.virtual_memory().percent

    def _render_impl(self) -> None:
        assert self.percentage is not None
        self._chart.addPoint(Colors.cpu_chart_line, self.percentage)
        self._chart.setLabel(f"RAM {self.percentage:.1f}%")
        self._chart.repaint()
