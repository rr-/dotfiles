from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.resources import ResourcesUpdater
from panel.widgets.base import BaseWidget
from panel.widgets.chart import Chart


class CpuWidget(BaseWidget):
    def __init__(
        self, updater: ResourcesUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._updater = updater

        self._chart = Chart(
            self, min_width=80, scale_low=0.0, scale_high=100.0
        )

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._chart)

        self._updater.cpu_usage_changed.connect(self._on_cpu_usage_change)

    def _on_cpu_usage_change(self, percentage: float) -> None:
        self._chart.addPoint(Colors.cpu_chart_line, percentage)
        self._chart.setLabel(f"CPU {percentage:.1f}%")
        self._chart.repaint()
