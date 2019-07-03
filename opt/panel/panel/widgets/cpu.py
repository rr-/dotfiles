from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.cpu import CpuUpdater
from panel.widgets.base import BaseWidget
from panel.widgets.chart import Chart


class CpuWidget(BaseWidget):
    def __init__(self, updater: CpuUpdater, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._updater = updater

        self._chart = Chart(
            self, min_width=80, scale_low=0.0, scale_high=100.0
        )

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._chart)

        self._updater.value_changed.connect(self._on_value_change)

    def _on_value_change(self, percentage: float) -> None:
        self._chart.addPoint(Colors.cpu_chart_line, percentage)
        self._chart.setLabel(f"CPU {percentage:.1f}%")
        self._chart.repaint()
