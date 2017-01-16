# pylint: disable=invalid-name
import subprocess
import alsaaudio
from PyQt5 import QtCore, QtGui, QtWidgets
from panel.widgets.widget import Widget


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
        height = self.height()
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
        painter.setBrush(QtGui.QColor('#AAA'))
        painter.drawPolygon(QtGui.QPolygon(poly))

        poly = [points['vol1'], points['vol2'], points['max1'], points['max2']]
        painter.setBrush(QtGui.QColor('#EEE'))
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.setPen(QtGui.QPen(QtGui.QColor('#888')))
        poly = [points['zero'], points['max1'], points['max2']]
        painter.setBrush(QtGui.QBrush())
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.end()


class VolumeWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.volume = None
        self.muted = False

        self._icon_label = QtWidgets.QLabel()
        self._volume_control = VolumeControl(QtCore.QSize(50, 10))

        container = QtWidgets.QWidget()
        container.mouseReleaseEvent = self.toggle_mute
        container.wheelEvent = self.change_volume
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=6))
        container.layout().addWidget(self._icon_label)
        container.layout().addWidget(self._volume_control)
        main_window[0].layout().addWidget(container)

    def change_volume(self, event):
        with self.exception_guard():
            subprocess.call([
                'amixer', '-q', 'set', 'Master',
                '1dB%s' % ['-', '+'][event.angleDelta().y() > 0],
                'unmute'])
            self.refresh()
            self.render()

    def toggle_mute(self, _event):
        with self.exception_guard():
            subprocess.call(['amixer', '-q', 'set', 'Master', 'toggle'])
            self.refresh()
            self.render()

    def refresh_impl(self):
        self.volume = alsaaudio.Mixer().getvolume()[0]
        self.muted = alsaaudio.Mixer().getmute()[0]

    def render_impl(self):
        self.set_icon(
            self._icon_label,
            'volume-off' if self.muted else 'volume-on')
        self._volume_control.set(self.volume)
        self._volume_control.repaint()
