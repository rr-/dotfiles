# pylint: disable=invalid-name
import collections
from PyQt5 import QtGui, QtWidgets


class Chart(QtWidgets.QWidget):
    def __init__(self, size):
        super().__init__()
        self.setMinimumSize(size)
        self.points = collections.defaultdict(list)

    def addPoint(self, color, y):
        self.points[color].append(y)

    def paintEvent(self, _event):
        width = self.width()
        height = self.height()

        highest = max(p for points in self.points.values() for p in points)

        margin = 3

        def x_transform(x):
            return margin \
                + width - 1 \
                - 2 * margin \
                - 2 * x

        def y_transform(y):
            return margin \
                + height - 1 \
                - 2 * margin \
                - y * (height - 1 - 2 * margin) / max(1, highest)

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.setBrush(QtGui.QBrush(QtGui.QColor('#EEE')))
        painter.setPen(QtGui.QPen(0))
        painter.drawRect(
            margin, margin, width - 2 * margin, height - 2 * margin)
        painter.setBrush(QtGui.QBrush())

        for color, points in self.points.items():
            painter.setPen(QtGui.QColor(color))
            prev_x = 0
            prev_y = points[-1]
            for x, y in enumerate(reversed(points)):
                dx = x_transform(x)
                excess = dx < margin
                if excess:
                    dx = margin
                painter.drawLine(
                    x_transform(prev_x),
                    y_transform(prev_y),
                    dx,
                    y_transform(y))
                prev_x = x
                prev_y = y
                if excess:
                    points.pop(0)
                    break

        painter.setPen(QtGui.QColor('#888'))
        painter.drawRect(
            margin - 1,
            margin - 1,
            width - 1 - 2 * (margin - 1),
            height - 1 - 2 * (margin - 1))

        painter.end()
