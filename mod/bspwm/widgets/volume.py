# pylint: disable=invalid-name
import subprocess
import alsaaudio
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import settings


class VolumeControl(QtWidgets.QWidget):
    def __init__(self, size):
        super().__init__()
        self.setMinimumSize(size)
        self.value = 0
        self.max = 100

    def set(self, value):
        self.value = value

    def paintEvent(self, _event):
        width = self.width()
        height = self.height() - settings.BOTTOM_BORDER
        margin_x = 3
        margin_y = 3
        inner_width = width - margin_x
        inner_height = height - 1 - 2 * margin_y

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        points = {
            'zero': QtCore.QPoint(margin_x, height - 1 - margin_y),
            'vol1': QtCore.QPoint(
                margin_x + self.value * inner_width / self.max,
                height - 1 - margin_y),
            'vol2': QtCore.QPoint(
                margin_x + self.value * inner_width / self.max,
                height - 1 - margin_y - self.value * inner_height / self.max),
            'max1': QtCore.QPoint(width - 1, margin_y),
            'max2': QtCore.QPoint(width - 1, height - 1 - margin_y),
        }

        poly = [points['zero'], points['vol1'], points['vol2']]
        painter.setPen(QtGui.QPen(0))
        painter.setBrush(QtGui.QColor('#999'))
        painter.drawPolygon(QtGui.QPolygon(poly))

        poly = [points['vol1'], points['vol2'], points['max1'], points['max2']]
        painter.setBrush(QtGui.QColor('#333'))
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.setPen(QtGui.QPen(QtGui.QColor('#999')))
        poly = [points['zero'], points['max1'], points['max2']]
        painter.setBrush(QtGui.QBrush())
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.end()


class VolumeProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.volume = None
        self.muted = False
        self._label = QtWidgets.QLabel()
        self._volume_control = VolumeControl(
            QtCore.QSize(50, main_window.height()))
        main_window[0].layout().addWidget(self._label)
        main_window[0].layout().addWidget(self._volume_control)
        for widget in [self._label, self._volume_control]:
            widget.mouseReleaseEvent = self.toggle_mute
            widget.wheelEvent = self.change_volume

    def change_volume(self, event):
        subprocess.call([
            'amixer', '-q', 'set', 'Master',
            '1dB%s' % ['-', '+'][event.angleDelta().y() > 0],
            'unmute'])
        self.refresh()
        self.render()

    def toggle_mute(self, _event):
        subprocess.call(['amixer', '-q', 'set', 'Master', 'toggle'])
        self.refresh()
        self.render()

    def refresh(self):
        self.volume = alsaaudio.Mixer().getvolume()[0]
        self.muted = alsaaudio.Mixer().getmute()[0]

    def render(self):
        if self.muted:
            self._label.setText('\U0001f507')
        else:
            self._label.setText('\U0001f50a')
        self._volume_control.set(self.volume)
        self._volume_control.repaint()
