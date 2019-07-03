import math
import os
import time

from PyQt5 import QtGui, QtWidgets

from panel.updaters.mpvmd import MpvmdUpdater
from panel.widgets.base import BaseWidget


def _format_time(seconds: int) -> str:
    seconds = math.floor(float(seconds))
    return "%02d:%02d" % (seconds // 60, seconds % 60)


class MpvmdWidget(BaseWidget):
    def __init__(
        self, updater: MpvmdUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._updater = updater
        self._last_updated = 0.0

        self._status_icon_label = QtWidgets.QLabel(self)
        self._song_label = QtWidgets.QLabel(self)
        self._shuffle_icon_label = QtWidgets.QLabel(self)

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=6)
        layout.addWidget(self._status_icon_label)
        layout.addWidget(self._song_label)
        layout.addWidget(self._shuffle_icon_label)

        self._status_icon_label.mouseReleaseEvent = self._play_pause_clicked
        self._song_label.mouseReleaseEvent = self._play_pause_clicked
        self._shuffle_icon_label.mouseReleaseEvent = self._shuffle_clicked
        self._status_icon_label.wheelEvent = self._prev_or_next_track
        self._song_label.wheelEvent = self._prev_or_next_track

        self._updater.is_paused_changed.connect(self._on_is_paused_change)
        self._updater.is_shuffle_enabled_changed.connect(
            self._on_is_shuffle_enabled_change
        )
        self._updater.elapsed_changed.connect(self._on_elapsed_change)
        self._updater.path_changed.connect(self._on_path_change)
        self._updater.metadata_changed.connect(self._on_metadata_change)
        self._on_is_paused_change(self._updater.is_paused)
        self._on_is_shuffle_enabled_change(self._updater.is_shuffle_enabled)

    def _play_pause_clicked(self, _event: QtGui.QMouseEvent) -> None:
        with self.exception_guard():
            self._updater.is_paused = not self._updater.is_paused

    def _prev_or_next_track(self, event: QtGui.QWheelEvent) -> None:
        with self.exception_guard():
            if event.angleDelta().y() > 0:
                self._updater.next_track()
            else:
                self._updater.prev_track()

    def _shuffle_clicked(self, _event: QtGui.QMouseEvent) -> None:
        with self.exception_guard():
            self._updater.is_shuffle_enabled = (
                not self._updater.is_shuffle_enabled
            )

    def _on_is_paused_change(self, is_paused: bool) -> None:
        self._set_icon(
            self._status_icon_label, "play" if is_paused else "pause"
        )

    def _on_is_shuffle_enabled_change(self, is_shuffle_enabled: bool) -> None:
        self._set_icon(
            self._shuffle_icon_label,
            "shuffle-on" if is_shuffle_enabled else "shuffle-off",
        )

    def _on_elapsed_change(self) -> None:
        if time.time() - self._last_updated >= 1:
            with self.exception_guard():
                self._update_text()

    def _on_path_change(self) -> None:
        with self.exception_guard():
            self._update_text()

    def _on_metadata_change(self) -> None:
        with self.exception_guard():
            self._update_text()

    def _update_text(self) -> None:
        text = ""
        if self._updater.metadata.get("title"):
            if self._updater.metadata.get("artist"):
                text = (
                    self._updater.metadata["artist"]
                    + " - "
                    + self._updater.metadata["title"]
                )
            else:
                text = self._updater.metadata["title"]
        elif self._updater.metadata.get("icy-title"):
            text = self._updater.metadata["icy-title"]
        else:
            text = os.path.basename(self._updater.path or "")

        if self._updater.elapsed and self._updater.duration:
            text += " %s / %s" % (
                _format_time(self._updater.elapsed),
                _format_time(self._updater.duration),
            )

        self._song_label.setText(text)
        self._last_updated = time.time()
