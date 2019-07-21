import glob
import typing as T
from pathlib import Path

import requests
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


class NetworkUpdater(BaseUpdater):
    updated = QtCore.pyqtSignal(int, int)

    def __init__(self) -> None:
        super().__init__()

        self.is_available = False
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
                    self.is_available = True
        except (FileNotFoundError, PermissionError):
            pass

        if self.is_available:
            self._old_rx_bytes = int(self._rx_path.read_text().strip())
            self._old_tx_bytes = int(self._tx_path.read_text().strip())
        else:
            self._old_rx_bytes = 0
            self._old_tx_bytes = 0

        timer = QtCore.QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self._on_timeout)
        if self.is_available:
            timer.start()
            self._on_timeout()

    def _on_timeout(self) -> None:
        rx_bytes = int(self._rx_path.read_text().strip())
        tx_bytes = int(self._tx_path.read_text().strip())
        net_in = rx_bytes - self._old_rx_bytes
        net_out = tx_bytes - self._old_tx_bytes
        self._old_rx_bytes = rx_bytes
        self._old_tx_bytes = tx_bytes
        self.updated.emit(net_in, net_out)
