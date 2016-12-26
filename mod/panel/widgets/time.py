from datetime import datetime
from PyQt5 import QtWidgets
from widgets.widget import Widget


class TimeWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.date = None
        self._date_label = QtWidgets.QLabel()
        self._clock_label = QtWidgets.QLabel()
        for widget in [self._date_label, self._clock_label]:
            main_window[0].layout().addWidget(widget)
        self._date_label.setStyleSheet(
            'QWidget { margin-left: 12px; margin-right: 0 }')
        self._clock_label.setStyleSheet(
            'QWidget { margin-left: 0; padding: 0 }')

    def refresh_impl(self):
        self.date = datetime.now()

    def render_impl(self):
        self._clock_label.setText(datetime.strftime(self.date, '%H:%M:%S'))
        self._date_label.setText(datetime.strftime(self.date, '%a, %d %b %Y'))
