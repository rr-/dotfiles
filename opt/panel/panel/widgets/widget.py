import logging
import time
import typing as T
from contextlib import contextmanager
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets

from panel.colors import Colors

ROOT_DIR = Path(__file__).parent.parent


class Widget:
    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        self.app = app
        self.main_window = main_window

    @contextmanager
    def exception_guard(self, sleep_time: int = 0) -> T.Generator:
        try:
            yield
        except Exception as ex:
            logging.exception(ex)
            time.sleep(sleep_time)

    @property
    def container(self) -> QtWidgets.QWidget:
        raise NotImplementedError("Not implemented")

    @property
    def available(self) -> bool:
        return True

    def refresh(self) -> None:
        with self.exception_guard(sleep_time=1):
            if not self.available:
                return
            self._refresh_impl()

    def render(self) -> None:
        with self.exception_guard():
            if not self.available:
                return
            self._render_impl()

    def _refresh_impl(self) -> None:
        raise NotImplementedError("Not implemented")

    def _render_impl(self) -> None:
        raise NotImplementedError("Not implemented")

    def _set_icon(self, widget: QtWidgets.QWidget, icon_name: str) -> None:
        if widget.property("icon_name") == icon_name:
            return
        widget.setProperty("icon_name", icon_name)

        icon_path = ROOT_DIR / "data" / "icons" / (icon_name + ".svg")
        target_size = QtCore.QSize(18, 18)
        icon_content = icon_path.read_bytes()
        icon_content = icon_content.replace(
            b"<svg", b'<svg fill="%s"' % Colors.foreground.encode("ascii")
        )

        svg_renderer = QtSvg.QSvgRenderer(icon_content)
        image = QtGui.QPixmap(target_size * self.app.devicePixelRatio())
        painter = QtGui.QPainter()

        image.fill(QtCore.Qt.transparent)

        painter.begin(image)
        svg_renderer.render(painter)
        painter.end()

        image.setDevicePixelRatio(self.app.devicePixelRatio())

        widget.setPixmap(image)
