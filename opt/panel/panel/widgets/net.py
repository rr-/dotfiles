import glob
import math
import typing as T
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from panel.colors import Colors
from panel.widgets.chart import Chart
from panel.widgets.widget import Widget


def convert_speed(speed_bytes: int) -> str:
    suffixes = ("B", "KB", "MB", "GB", "TB")
    if speed_bytes < 1024:
        return "{:.0f} {}".format(speed_bytes, suffixes[0])
    power = int(math.floor(math.log(speed_bytes, 1024)))
    denominator = math.pow(1024, power)
    return f"{speed_bytes / denominator:.0f} {suffixes[power]}"


class NetworkUsageWidget(Widget):
    delay = 1

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)
        self.net_in = 0
        self.net_out = 0
        self._old_rx_bytes = 0
        self._old_tx_bytes = 0

        available = False
        try:
            self._rx_path: T.Optional[Path] = None
            self._tx_path: T.Optional[Path] = None
            for path in Path("/sys/class/net/").iterdir():
                if "virtual" in str(path.resolve()):
                    continue
                state = (path / "operstate").read_text().strip()
                if state.lower() == "up":
                    self._rx_path = path / "statistics" / "rx_bytes"
                    self._tx_path = path / "statistics" / "tx_bytes"
                    available = True
        except Exception:
            pass

        if available:
            self._old_rx_bytes = int(self._rx_path.read_text().strip())
            self._old_tx_bytes = int(self._tx_path.read_text().strip())

        self._container = QtWidgets.QWidget(main_window)
        self._chart = Chart(
            self._container,
            min_width=120,
            scale_low=0.0,
            scale_high=1024.0 * 1024.0,
        )

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._chart)

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    @property
    def available(self) -> bool:
        return self._rx_path is not None and self._tx_path is not None

    def _refresh_impl(self) -> None:
        rx_bytes = int(self._rx_path.read_text().strip())
        tx_bytes = int(self._tx_path.read_text().strip())
        self.net_in = rx_bytes - self._old_rx_bytes
        self.net_out = tx_bytes - self._old_tx_bytes
        self._old_rx_bytes = rx_bytes
        self._old_tx_bytes = tx_bytes

    def _render_impl(self) -> None:
        self._chart.setLabel(
            f"DL {convert_speed(self.net_in)}  UL {convert_speed(self.net_out)}"
        )
        self._chart.addPoint(Colors.net_up_chart_line, self.net_in)
        self._chart.addPoint(Colors.net_down_chart_line, self.net_out)
        self._chart.update()
