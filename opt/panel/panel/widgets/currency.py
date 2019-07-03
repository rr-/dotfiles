from PyQt5 import QtWidgets

from panel.colors import Colors
from panel.updaters.currency import CurrencyUpdater
from panel.widgets.chart import Chart


class CurrencyWidget(Chart):
    def __init__(
        self, updater: CurrencyUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(
            parent, min_width=80, scale_low=float("inf"), scale_high=0.0
        )
        self._updater = updater

        self._updater.quotes_changed.connect(self._on_quotes_change)
        self._on_quotes_change()

    def _on_quotes_change(self) -> None:
        self.clearPoints()

        value = 0
        for key, value in sorted(
            self._updater.quotes.items(), key=lambda kv: kv[0]
        ):
            self.addPoint(Colors.currency_chart_line, value)

        self.setLabel(f"USD {value}")
        self.update()
