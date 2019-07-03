import glob
import typing as T
from pathlib import Path

from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


def glob_path(pattern: str) -> T.Optional[Path]:
    try:
        return Path(glob.glob(pattern)[0])
    except IndexError:
        return None


class BatteryUpdater(BaseUpdater):
    updated = QtCore.pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()
        self.precentage = 0.0

        self._charge_now_path = glob_path(
            "/sys/class/power_supply/*/energy_now"
        )
        self._charge_max_path = glob_path(
            "/sys/class/power_supply/*/energy_full"
        )

        if self.is_available:
            timer = QtCore.QTimer(self)
            timer.setInterval(10000)
            timer.timeout.connect(self._on_timeout)
            timer.start()

            self._on_timeout()

    @property
    def is_available(self) -> bool:
        return (
            self._charge_now_path is not None
            and self._charge_max_path is not None
        )

    def _on_timeout(self) -> None:
        assert self._charge_now_path
        assert self._charge_max_path
        current_value = int(self._charge_now_path.read_text())
        max_value = int(self._charge_max_path.read_text())
        self.percentage = current_value * 100.0 / max_value
        self.updated.emit(self.percentage)
