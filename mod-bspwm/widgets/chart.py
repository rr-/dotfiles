import collections
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import settings

class Chart(QtWidgets.QWidget):
    def __init__(self, size):
        super().__init__()
        self.setMinimumSize(size)
        self.points = collections.defaultdict(list)

    def addPoint(self, color, y):
        self.points[color].append(y)

    def paintEvent(self, e):
        width = self.width()
        height = self.height() - settings.BOTTOM_BORDER

        if not self.points:
            return
        highest = max(p for points in self.points.values() for p in points)
        if highest == 0:
            return

        margin = 3

        x_transform = lambda x: \
            margin \
            + width - 1 \
            - 2 * margin \
            - 2 * x

        y_transform = lambda y: \
            margin \
            + height - 1 \
            - 2 * margin \
            - y * (height - 1 - 2 * margin) / highest

        qp = QtGui.QPainter()
        qp.begin(self)

        qp.setBrush(QtGui.QBrush(QtGui.QColor('#333')))
        qp.setPen(QtGui.QPen(0))
        qp.drawRect(margin, margin, width - 2 * margin, height - 2 * margin)
        qp.setBrush(QtGui.QBrush())

        for color, points in self.points.items():
            qp.setPen(QtGui.QColor(color))
            size = self.size()
            ox = 0
            oy = points[-1]
            for x, y in enumerate(reversed(points)):
                dx = x_transform(x)
                excess = dx < margin
                if excess:
                    dx = margin
                qp.drawLine(x_transform(ox), y_transform(oy), dx, y_transform(y))
                ox = x
                oy = y
                if excess:
                    points.pop(0)
                    break

        qp.setPen(QtGui.QColor('#808080'))
        qp.drawRect(margin - 1, margin - 1, width - 1 - 2 * (margin - 1), height - 1 - 2 * (margin - 1))

        qp.end()
