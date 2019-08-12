import datetime
import time
import typing as T

import requests
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater
from panel.util import exception_guard


class CurrencyUpdaterThread(QtCore.QThread):
    updated = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.running = False
        self.quotes: T.Dict[datetime.datetime, float] = {}

    def run(self) -> None:
        self.running = True
        while self.running:
            response = requests.get(
                "https://www.ingturbo.pl/services/underlying/usd-pln/chart"
                "?period=intraday"
            )
            response.raise_for_status()

            for row in response.json()["Quotes"]:
                _time, quote = row
                date = datetime.datetime.fromtimestamp(_time / 1000.0)
                self.quotes[date] = quote

            self.updated.emit(self.quotes)
            time.sleep(60)


class CurrencyUpdater(BaseUpdater):
    quotes_changed = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._thread = CurrencyUpdaterThread(self)
        self._thread.updated.connect(self.quotes_changed.emit)
        self.quotes = self._thread.quotes
        self._thread.start()
