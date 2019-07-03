from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.resources import ResourcesUpdater
from panel.widgets.base import BaseWidget
from panel.widgets.chart import Chart


class MemoryWidget(BaseWidget):
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

        self._updater.ram_usage_changed.connect(self._on_ram_usage_change)

    def _on_ram_usage_change(self, percentage: float) -> None:
        self._chart.addPoint(Colors.memory_chart_line, percentage)
        self._chart.setLabel(f"RAM {percentage:.1f}%")
        self._chart.repaint()
