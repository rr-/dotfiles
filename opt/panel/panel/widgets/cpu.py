from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.resources import ResourcesUpdater
from panel.widgets.chart import Chart


class CpuWidget(Chart):
    def __init__(
        self, updater: ResourcesUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent, min_width=80, scale_low=0.0, scale_high=100.0)
        self._updater = updater
        self._updater.cpu_usage_changed.connect(self._on_cpu_usage_change)

    def _on_cpu_usage_change(self, percentage: float) -> None:
        self.addPoint(Colors.cpu_chart_line, percentage)
        self.setLabel(f"CPU {percentage:.1f}%")
        self.update()
