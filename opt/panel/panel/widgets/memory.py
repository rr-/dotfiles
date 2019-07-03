from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.resources import ResourcesUpdater
from panel.widgets.chart import Chart


class MemoryWidget(Chart):
    def __init__(
        self, updater: ResourcesUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent, min_width=80, scale_low=0.0, scale_high=100.0)
        self._updater = updater
        self._updater.ram_usage_changed.connect(self._on_ram_usage_change)

    def _on_ram_usage_change(self, percentage: float) -> None:
        self.addPoint(Colors.memory_chart_line, percentage)
        self.setLabel(f"RAM {percentage:.1f}%")
        self.update()
