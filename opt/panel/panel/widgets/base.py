import logging
import re
import typing as T
from contextlib import contextmanager
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets

from panel.colors import Colors

ROOT_DIR = Path(__file__).parent.parent
ICON_STYLESHEET = """
polygon {{ fill: {foreground} }}
path {{ fill: {foreground} }}
.off {{ opacity: 0.3; }}
"""


class BaseWidget(QtWidgets.QWidget):
    @contextmanager
    def exception_guard(self) -> T.Generator:
        try:
            yield
        except Exception as ex:
            logging.exception(ex)

    def _set_icon(self, widget: QtWidgets.QWidget, icon_name: str) -> None:
        if widget.property("icon_name") == icon_name:
            return
        widget.setProperty("icon_name", icon_name)

        icon_path = ROOT_DIR / "data" / "icons" / (icon_name + ".svg")
        target_size = QtCore.QSize(18, 18)
        stylesheet = ICON_STYLESHEET.format(foreground=Colors.foreground)
        scale_factor = QtWidgets.QApplication.instance().devicePixelRatio()

        icon_content = icon_path.read_text()
        icon_content = re.sub(
            "(<svg.*>)",
            r"\1<style type='text/css'>" + stylesheet + "</style>",
            icon_content,
        )

        svg_renderer = QtSvg.QSvgRenderer(icon_content.encode("utf-8"))
        image = QtGui.QPixmap(target_size * scale_factor)
        image.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter()
        painter.begin(image)
        svg_renderer.render(painter)
        painter.end()

        image.setDevicePixelRatio(scale_factor)

        widget.setPixmap(image)
