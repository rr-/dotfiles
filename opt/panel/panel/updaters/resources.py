import psutil
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


class ResourcesUpdater(BaseUpdater):
    cpu_usage_changed = QtCore.pyqtSignal(float)
    ram_usage_changed = QtCore.pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()

        timer = QtCore.QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self._on_timeout)
        timer.start()

    def _on_timeout(self) -> None:
        self.cpu_usage_changed.emit(psutil.cpu_percent(interval=None))
        self.ram_usage_changed.emit(psutil.virtual_memory().percent)
