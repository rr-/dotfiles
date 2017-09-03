from datetime import datetime
from PyQt5 import QtWidgets
from panel.widgets.widget import Widget


class TimeWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.date = None

        self._container = QtWidgets.QWidget(main_window, objectName='time')
        self._date_label = QtWidgets.QLabel(self._container)
        self._clock_label = QtWidgets.QLabel(self._container)

        layout = QtWidgets.QHBoxLayout(self._container, spacing=12, margin=0)
        layout.addWidget(self._date_label)
        layout.addWidget(self._clock_label)

    @property
    def container(self):
        return self._container

    def _refresh_impl(self):
        self.date = datetime.now()

    def _render_impl(self):
        self._clock_label.setText(datetime.strftime(self.date, '%H:%M:%S'))
        self._date_label.setText(datetime.strftime(self.date, '%a, %d %b %Y'))
