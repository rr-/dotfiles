import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from panel.updaters.window_title import WindowTitleUpdater
from panel.widgets.base import BaseWidget

DEFAULT_TITLE = "<no window id>"


class WindowTitleWidget(BaseWidget):
    def __init__(
        self, updater: WindowTitleUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._updater = updater

        self._label = QtWidgets.QLabel(self)
        self._label.setProperty("class", "wintitle")

        layout = QtWidgets.QHBoxLayout(self, spacing=12, margin=0)
        layout.addWidget(self._label)

        self._max_width = parent.width() * 0.8
        self._font_metrics = QtGui.QFontMetrics(self._label.font())

        self._updater.updated.connect(self._on_update)
        self._on_update(None)

    def _on_update(self, window_title: T.Optional[str]) -> None:
        self._label.setText(
            self._font_metrics.elidedText(
                window_title or DEFAULT_TITLE,
                QtCore.Qt.ElideRight,
                self._max_width,
            )
        )
