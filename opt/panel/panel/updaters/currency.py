import datetime
import typing as T

import requests
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


class CurrencyUpdater(BaseUpdater):
    quotes_changed = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        timer = QtCore.QTimer(self)
        timer.setInterval(60000)
        timer.timeout.connect(self._on_timeout)
        timer.start()

        self.quotes: T.Dict[datetime.datetime, float] = {}
        self._on_timeout()

    def _on_timeout(self) -> None:
        response = requests.get(
            "https://www.ingturbo.pl/services/underlying/usd-pln/chart"
            "?period=intraday"
        )
        response.raise_for_status()

        for row in response.json()["Quotes"]:
            time, quote = row
            date = datetime.datetime.fromtimestamp(time / 1000.0)
            self.quotes[date] = quote

        self.quotes_changed.emit()
