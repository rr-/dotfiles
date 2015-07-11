from datetime import datetime, timedelta
from PyQt4 import QtGui

class TimeProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.date_label = QtGui.QLabel()
        self.clock_label = QtGui.QLabel()
        for w in [self.date_label, self.clock_label]:
            main_window[0].right_widget.layout().addWidget(w)
        self.date_label.setStyleSheet('QWidget { margin-left: 12px; margin-right: 0 }')
        self.clock_label.setStyleSheet('QWidget { margin-left: 0; padding: 0 }')

    def refresh(self):
        self.date = datetime.now()

    def render(self):
        self.clock_label.setText(datetime.strftime(self.date, '%H:%M:%S'))
        self.date_label.setText(datetime.strftime(self.date, '%a, %d %b %Y'))
