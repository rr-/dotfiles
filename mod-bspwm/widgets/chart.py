from PyQt4 import QtGui
import collections

class Chart(QtGui.QWidget):
    def __init__(self, size):
        super().__init__()
        self.setMinimumSize(size)
        self.points = collections.defaultdict(list)

    def addPoint(self, color, y):
        self.points[color].append(y)

    def paintEvent(self, e):
        if not self.points:
            return
        highest = max(p for points in self.points.values() for p in points)
        if highest == 0:
            return

        margin = 3
        x_transform = lambda x: margin + self.width() - 1 - 2 * margin - 2 * x
        y_transform = lambda y: margin + self.height() - 1 - 2 * margin - y * (size.height() - 1 - 2 * margin) / highest

        qp = QtGui.QPainter()
        qp.begin(self)
        for color, points in self.points.items():
            qp.setPen(QtGui.QColor(color))
            size = self.size()
            ox = 0
            oy = points[-1]
            for x, y in enumerate(reversed(points[0:-2])):
                if x_transform(x) <= margin:
                    points.pop(0)
                    break
                qp.drawLine(x_transform(ox), y_transform(oy), x_transform(x), y_transform(y))
                ox = x
                oy = y

        margin -= 1
        qp.setPen(QtGui.QColor('#444444'))
        qp.drawRect(margin, margin, self.width() - 1 - 2 * margin, self.height() - 1 - 2 * margin)

        qp.end()
