import math

from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.network import NetworkUpdater
from panel.widgets.base import BaseWidget
from panel.widgets.chart import Chart


def convert_speed(speed_bytes: int) -> str:
    suffixes = ("B", "KB", "MB", "GB", "TB")
    if speed_bytes < 1024:
        return "{:.0f} {}".format(speed_bytes, suffixes[0])
    power = int(math.floor(math.log(speed_bytes, 1024)))
    denominator = math.pow(1024, power)
    return f"{speed_bytes / denominator:.0f} {suffixes[power]}"


class NetworkUsageWidget(BaseWidget):
    def __init__(
        self, updater: NetworkUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._updater = updater

        self._chart = Chart(
            self, min_width=120, scale_low=0.0, scale_high=1024.0 * 1024.0
        )

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._chart)

        self._updater.updated.connect(self._on_update)

    def _on_update(self, net_in: int, net_out: int) -> None:
        self._chart.setLabel(
            f"DL {convert_speed(net_in)}  UL {convert_speed(net_out)}"
        )
        self._chart.addPoint(Colors.net_up_chart_line, net_in)
        self._chart.addPoint(Colors.net_down_chart_line, net_out)
        self._chart.update()
