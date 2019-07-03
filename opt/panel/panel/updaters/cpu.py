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


class CpuUpdater(BaseUpdater):
    def __init__(self) -> None:
        super().__init__()
        self.thread = CpuUpdaterThread(self)
        self.thread.start()
        self.value_changed = self.thread.value_changed
