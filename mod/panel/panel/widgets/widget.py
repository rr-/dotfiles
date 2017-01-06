import os
import time
import logging
from PyQt5 import QtCore, QtGui, QtSvg


class Widget:
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window

    def refresh(self):
        try:
            self.refresh_impl()
        except Exception as ex:
            logging.exception(ex)
            time.sleep(1)

    def render(self):
        try:
            self.render_impl()
        except Exception as ex:
            logging.error(ex)
            time.sleep(1)

    def refresh_impl(self):
        raise NotImplementedError()

    def render_impl(self):
        raise NotImplementedError()

    def set_icon(self, widget, icon_name):
        if widget.property('icon_name') == icon_name:
            return
        widget.setProperty('icon_name', icon_name)

        icon_path = os.path.join(
            os.path.dirname(__file__), os.pardir, 'icons', icon_name + '.svg')
        target_size = QtCore.QSize(18, 18)

        svg_renderer = QtSvg.QSvgRenderer(icon_path)
        image = QtGui.QPixmap(target_size * self.app.devicePixelRatio())
        painter = QtGui.QPainter()

        image.fill(QtCore.Qt.transparent)

        painter.begin(image)
        svg_renderer.render(painter)
        painter.end()

        image.setDevicePixelRatio(self.app.devicePixelRatio())

        widget.setPixmap(image)
