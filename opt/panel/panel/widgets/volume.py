from PyQt5 import QtCore, QtGui, QtWidgets

from panel.colors import Colors
from panel.updaters.volume import VolumeUpdater
from panel.widgets.base import BaseWidget


class VolumeControl(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, size: QtCore.QSize) -> None:
        super().__init__(parent)
        self.setMinimumSize(size)
        self.value = 0
        self.max = 100

    def set(self, value: int) -> None:
        self.value = value
        self.update()

    def paintEvent(self, _event: QtGui.QPaintEvent) -> None:
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
            "zero": QtCore.QPoint(margin_x, height - 1 - margin_y),
            "vol1": QtCore.QPoint(
                margin_x + self.value * inner_width / self.max,
                height - 1 - margin_y,
            ),
            "vol2": QtCore.QPoint(
                margin_x + self.value * inner_width / self.max,
                height - 1 - margin_y - self.value * inner_height / self.max,
            ),
            "max1": QtCore.QPoint(width - 1, margin_y),
            "max2": QtCore.QPoint(width - 1, height - 1 - margin_y),
        }

        poly = [points["zero"], points["vol1"], points["vol2"]]
        painter.setPen(QtGui.QPen(0))
        painter.setBrush(QtGui.QColor(Colors.volume_chart_background))
        painter.drawPolygon(QtGui.QPolygon(poly))

        poly = [points["vol1"], points["vol2"], points["max1"], points["max2"]]
        painter.setBrush(QtGui.QColor(Colors.chart_background))
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.setPen(QtGui.QPen(QtGui.QColor(Colors.chart_foreground)))
        poly = [points["zero"], points["max1"], points["max2"]]
        painter.setBrush(QtGui.QBrush())
        painter.drawPolygon(QtGui.QPolygon(poly))

        painter.end()


class VolumeWidget(BaseWidget):
    def __init__(
        self, updater: VolumeUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)

        self._updater = updater
        self._updater.volume_changed.connect(self._on_volume_change)
        self._updater.mute_changed.connect(self._on_mute_change)

        self._icon_label = QtWidgets.QLabel(self)
        self._volume_control = VolumeControl(self, QtCore.QSize(50, 10))

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._volume_control)

        self._on_mute_change()
        self._on_volume_change()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        with self.exception_guard():
            self._updater.volume += 1 if event.angleDelta().y() > 0 else -1

    def mouseReleaseEvent(self, _event: QtGui.QMouseEvent) -> None:
        with self.exception_guard():
            self._updater.is_muted = not self._updater.is_muted

    def _on_mute_change(self) -> None:
        with self.exception_guard():
            self._set_icon(
                self._icon_label,
                "volume-off" if self._updater.is_muted else "volume-on",
            )

    def _on_volume_change(self) -> None:
        with self.exception_guard():
            self._volume_control.set(self._updater.volume)
