from PyQt4 import QtGui
import alsaaudio

class VolumeProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.label = QtGui.QLabel()
        main_window[0].right_widget.layout().addWidget(self.label)

    def refresh(self):
        self.volume = alsaaudio.Mixer().getvolume()[0]
        self.muted = alsaaudio.Mixer().getmute()[0]

    def render(self):
        if self.muted:
            self.label.setText('Volume: %5.02f (muted)' % self.volume)
        else:
            self.label.setText('Volume: %5.02f' % self.volume)
