from datetime import datetime
from PyQt5 import QtWidgets
from panel.widgets.widget import Widget


class TimeWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.date = None
        self._date_label = QtWidgets.QLabel()
        self._clock_label = QtWidgets.QLabel()
        wrapper_widget = QtWidgets.QFrame()
        wrapper_widget.setObjectName('time')
        wrapper_widget.setLayout(QtWidgets.QHBoxLayout(spacing=12, margin=0))
        wrapper_widget.layout().addWidget(self._date_label)
        wrapper_widget.layout().addWidget(self._clock_label)
        main_window[0].layout().addWidget(wrapper_widget)

    def refresh_impl(self):
        self.date = datetime.now()

    def render_impl(self):
        self._clock_label.setText(datetime.strftime(self.date, '%H:%M:%S'))
        self._date_label.setText(datetime.strftime(self.date, '%a, %d %b %Y'))
