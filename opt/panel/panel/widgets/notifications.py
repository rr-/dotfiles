from PyQt5 import QtCore, QtGui, QtWidgets

from panel.updaters.notifications import Notification, NotificationsUpdater
from panel.widgets.base import BaseWidget


class NotificationsAreaWidget(QtWidgets.QDialog):
    def __init__(
        self, parent: QtWidgets.QWidget, align_widget: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._align_widget = align_widget

        self.setWindowFlags(
            QtCore.Qt.Tool
            | QtCore.Qt.SplashScreen
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.X11BypassWindowManagerHint
        )
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)

        pos = self.parent().mapToGlobal(
            self._align_widget.geometry().bottomRight()
        )

        pos.setX(pos.x() - self.width())
        self.move(pos)


class NotificationWidget(QtWidgets.QLabel):
    def __init__(
        self, notification: Notification, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self.setText((notification.body or notification.summary).strip())
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(notification.duration.total_seconds() * 1000)
        timer.timeout.connect(self.remove)
        timer.start()

    def remove(self) -> None:
        self.parent().layout().removeWidget(self)
        if not self.parent().layout().count():
            self.parent().hide()
        self.deleteLater()


class NotificationsWidget(BaseWidget):
    def __init__(
        self,
        notifications_updater: NotificationsUpdater,
        parent: QtWidgets.QWidget,
    ) -> None:
        super().__init__(parent)
        self._updater = notifications_updater

        self._icon_label = QtWidgets.QLabel(self)
        self._icon_label.mouseReleaseEvent = self.toggle_enable
        self._area = NotificationsAreaWidget(
            self._icon_label.parent(), self._icon_label
        )

        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=0)
        layout.addWidget(self._icon_label)

        self._is_enabled = True
        self._updater.notified.connect(self._on_notify)
        self._update_icon()

    def toggle_enable(self, _event: QtGui.QMouseEvent) -> None:
        self._is_enabled = not self._is_enabled
        self._update_icon()

    def _update_icon(self) -> None:
        self._set_icon(
            self._icon_label, "bell-on" if self._is_enabled else "bell-off"
        )

    def _on_notify(self, notification: Notification) -> None:
        if not self._is_enabled:
            return
        widget = NotificationWidget(notification, self._area)
        self._area.layout().addWidget(widget)
        self._area.show()
