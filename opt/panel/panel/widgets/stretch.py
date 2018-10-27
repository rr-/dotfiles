from PyQt5 import QtWidgets

from panel.widgets.widget import Widget


class StretchWidget(Widget):
    delay = 1000

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)
        self._container = QtWidgets.QWidget()
        self._container.setProperty('class', 'stretch')
        self._container.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    def _refresh_impl(self) -> None:
        pass

    def _render_impl(self) -> None:
        pass
