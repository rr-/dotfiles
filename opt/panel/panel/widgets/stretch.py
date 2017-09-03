from panel.widgets.widget import Widget
from PyQt5 import QtWidgets


class StretchWidget(Widget):
    delay = 1000

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self._container = QtWidgets.QWidget()
        self._container.setProperty('class', 'stretch')
        self._container.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)

    @property
    def container(self):
        return self._container

    def _refresh_impl(self):
        pass

    def _render_impl(self):
        pass
