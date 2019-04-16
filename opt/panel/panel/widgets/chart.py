# pylint: disable=invalid-name
import collections
import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from panel.colors import Colors


class Chart(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        min_width: int,
        scale_low: float,
        scale_high: float,
    ) -> None:
        super().__init__(parent)
        self.setMinimumSize(QtCore.QSize(min_width, 0))
        self.scale_low = scale_low
        self.scale_high = scale_high
        self.label: T.Optional[str] = None
        self.points: T.Dict[str, T.List[float]] = collections.defaultdict(list)
        self.setProperty("class", "chart")

    def setLabel(self, text: T.Optional[str]) -> None:
        self.label = text

    def clearPoints(self) -> None:
        self.points.clear()

    def addPoint(self, color: str, y: float) -> None:
        self.points[color].append(y)

    def paintEvent(self, _event: QtGui.QPaintEvent) -> None:
        width = T.cast(int, self.width())
        height = T.cast(int, self.height())

        max_x = width
        max_y = height

        def x_transform(x: float) -> float:
            return max_x - x

        # trim excess data points
        for _, points in self.points.items():
            start_removing = False
            for x, _ in enumerate(reversed(points)):
                if start_removing:
                    points.pop(0)
                else:
                    dx = x_transform(x)
                    if dx < 0:
                        start_removing = True

        values = [p for points in self.points.values() for p in points]
        value_low = min(values + [self.scale_low])
        value_high = max(values + [self.scale_high])

        def y_transform(value: float) -> float:
            if value_high - value_low == 0:
                return max_y
            ratio = (value - value_low) / (value_high - value_low)
            return (1 - ratio) * max_y

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(Colors.chart_background)))
        painter.setPen(QtGui.QPen(0))
        painter.drawRect(0, 0, width - 1, height - 1)
        painter.setBrush(QtGui.QBrush())

        for color_name, points in self.points.items():
            polyline = []
            for x, y in enumerate(reversed(points)):
                dx = max(0.0, x_transform(x))
                dy = y_transform(y)
                polyline.append((dx, dy))

            polygon = polyline[:]
            polygon.insert(0, (max_x, max_y))
            polygon.append((polygon[-1][0], max_y))

            painter.setPen(QtGui.QPen())
            color = QtGui.QColor(color_name)
            color.setAlpha(75)
            painter.setBrush(color)
            painter.drawPolygon(
                QtGui.QPolygon(QtCore.QPoint(x, y) for x, y in polygon)
            )

            painter.setPen(QtGui.QColor(color_name))
            painter.drawPolyline(
                QtGui.QPolygon(QtCore.QPoint(x, y) for x, y in polyline)
            )

        if self.label:
            font = painter.font()
            font.setPixelSize(10)
            painter.setFont(font)
            painter.setPen(QtGui.QColor(Colors.foreground))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.label)

        painter.end()
