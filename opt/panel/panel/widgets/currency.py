import typing as T
import datetime
import requests

from PyQt5 import QtCore, QtWidgets

from panel.colors import Colors
from panel.widgets.chart import Chart
from panel.widgets.widget import Widget


class CurrencyWidget(Widget):
    delay = 60

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)
        self.percentage: T.Optional[float] = None
        self._container = QtWidgets.QWidget(main_window)
        self._chart = Chart(
            self._container,
            min_width=80,
            scale_low=float("inf"),
            scale_high=0.0,
        )

        self._quotes: T.Dict[datetime.datetime, float] = {}

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._chart)

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    def _refresh_impl(self) -> None:
        response = requests.get(
            "https://www.ingturbo.pl/services/underlying/usd-pln/chart"
            "?period=intraday"
        )
        response.raise_for_status()

        for row in response.json()["Quotes"]:
            time, quote = row
            date = datetime.datetime.fromtimestamp(time / 1000.0)
            self._quotes[date] = quote

        self._chart.clearPoints()
        for key, value in sorted(self._quotes.items(), key=lambda kv: kv[0]):
            self._chart.addPoint(Colors.cpu_chart_line, value)

        self._chart.setLabel(f"USD {value}")

    def _render_impl(self) -> None:
        self._chart.repaint()
