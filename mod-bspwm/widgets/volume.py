from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import alsaaudio
import subprocess

class VolumeControl(QtWidgets.QWidget):
    def __init__(self, size):
        super().__init__()
        self.setMinimumSize(size)
        self.value = 0
        self.max = 100

    def set(self, value):
        self.value = value

    def paintEvent(self, e):
        width = self.width()
        height = self.height() - BOTTOM_BORDER

        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)

        left_margin = 3
        vert_margin = 3
        points = {
            'zero': QtCore.QPoint(left_margin, height - 1 - vert_margin),
            'vol1': QtCore.QPoint(left_margin + self.value * (width - left_margin) / self.max, height - 1 - vert_margin),
            'vol2': QtCore.QPoint(left_margin + self.value * (width - left_margin) / self.max, height - 1 - vert_margin - self.value * (height - 1 - 2 * vert_margin) / self.max),
            'max1': QtCore.QPoint(width - 1, vert_margin),
            'max2': QtCore.QPoint(width - 1, height - 1 - vert_margin),
        }

        poly = [points['zero'], points['vol1'], points['vol2']]
        qp.setPen(QtGui.QPen(0))
        qp.setBrush(QtGui.QColor('#888'))
        qp.drawPolygon(QtGui.QPolygon(poly))

        poly = [points['vol1'], points['vol2'], points['max1'], points['max2']]
        qp.setBrush(QtGui.QColor('#333'))
        qp.drawPolygon(QtGui.QPolygon(poly))

        qp.setPen(QtGui.QPen(QtGui.QColor('#777')))
        poly = [points['zero'], points['max1'], points['max2']]
        qp.setBrush(QtGui.QBrush())
        qp.drawPolygon(QtGui.QPolygon(poly))

        qp.end()

class VolumeProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.label = QtWidgets.QLabel()
        self.volume_control = VolumeControl(QtCore.QSize(50, main_window.height()))
        main_window[0].right_widget.layout().addWidget(self.label)
        main_window[0].right_widget.layout().addWidget(self.volume_control)
        for w in [self.label, self.volume_control]:
            w.mouseReleaseEvent = self.toggle_mute
            w.wheelEvent = self.change_volume

    def change_volume(self, event):
        subprocess.call(['amixer', '-q', 'set', 'Master',
            '1dB%s' % ['-', '+'][event.angleDelta().y() > 0], 'unmute'])
        self.refresh()
        self.render()

    def toggle_mute(self, event):
        subprocess.call(['amixer', '-q', 'set', 'Master', 'toggle'])
        self.refresh()
        self.render()

    def refresh(self):
        self.volume = alsaaudio.Mixer().getvolume()[0]
        self.muted = alsaaudio.Mixer().getmute()[0]

    def render(self):
        if self.muted:
            self.label.setText('\U0001f507')
        else:
            self.label.setText('\U0001f50a')
        self.volume_control.set(self.volume)
        self.volume_control.repaint()
