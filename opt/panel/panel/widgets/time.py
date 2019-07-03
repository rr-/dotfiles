from datetime import datetime

from PyQt5 import QtCore, QtWidgets

from panel.widgets.base import BaseWidget


class TimeWidget(BaseWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent, objectName="time")
        self.date = datetime.now()

        self._date_label = QtWidgets.QLabel(self)
        self._clock_label = QtWidgets.QLabel(self)

        layout = QtWidgets.QHBoxLayout(self, spacing=12, margin=0)
        layout.addWidget(self._date_label)
        layout.addWidget(self._clock_label)

        timer = QtCore.QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self._on_timeout)
        timer.start()

        self._on_timeout()

    def _on_timeout(self) -> None:
        self.date = datetime.now()
        self._clock_label.setText(datetime.strftime(self.date, "%H:%M:%S"))
        self._date_label.setText(datetime.strftime(self.date, "%a, %d %b %Y"))
