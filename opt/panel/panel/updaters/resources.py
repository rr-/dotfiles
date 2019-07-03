import psutil
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


class CpuUpdaterThread(QtCore.QThread):
    value_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.running = False

    def run(self) -> None:
        value = psutil.cpu_percent(interval=0.1)
        self.value_changed.emit(value)

        self.running = True
        while self.running:
            value = psutil.cpu_percent(interval=1)
            self.value_changed.emit(value)


class ResourcesUpdater(BaseUpdater):
    ram_usage_changed = QtCore.pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()

        self.cpu_thread = CpuUpdaterThread(self)
        self.cpu_thread.start()

        self.cpu_usage_changed = self.cpu_thread.value_changed

        timer = QtCore.QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self._on_timeout)
        timer.start()

    def _on_timeout(self) -> None:
        self.ram_usage_changed.emit(psutil.virtual_memory().percent)
