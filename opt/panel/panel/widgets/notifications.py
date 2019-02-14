import threading
import typing as T
from dataclasses import dataclass
from datetime import timedelta

import dbus
import dbus.service
import Xlib
from PyQt5 import QtCore, QtGui, QtWidgets

from panel.widgets.widget import Widget

MIN_DURATION = timedelta(milliseconds=5000)
MAX_DURATION = timedelta(milliseconds=10000)


@dataclass
class Notification:
    id_: int
    summary: str
    body: str
    duration: timedelta


class NotificationsQueue:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.notifications: T.List[Notification] = []

    def get(self) -> T.Optional[Notification]:
        with self.lock:
            if self.notifications:
                return self.notifications.pop()
            return None

    def add(self, notification: Notification) -> None:
        with self.lock:
            for n in self.notifications:
                if n.id_ == notification.id_:
                    n.summary = notification.summary
                    n.body = notification.body
                    return

            self.notifications.append(notification)


class NotificationFetcher(dbus.service.Object):
    _id = 0

    def __init__(self, queue: NotificationsQueue) -> None:
        self._queue = queue
        self._disp = Xlib.display.Display()
        self._root = self._disp.screen().root
        self._NET_ACTIVE_WINDOW = self._disp.intern_atom("_NET_ACTIVE_WINDOW")

        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(
            "org.freedesktop.Notifications", bus=session_bus
        )
        super().__init__(bus_name, "/org/freedesktop/Notifications")

    def _get_active_window(self) -> int:
        response = self._root.get_full_property(
            self._NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType
        )
        if response:
            return int(response.value[0])
        return -1

    @dbus.service.method(
        "org.freedesktop.Notifications",
        in_signature="susssasa{ss}i",
        out_signature="u",
    )
    def Notify(
        self,
        app_name: str,
        notification_id: int,
        app_icon: str,
        summary: str,
        body: str,
        actions: T.List[str],
        hints: T.List[T.Tuple[str, str]],
        expire_timeout: int,
    ):
        wid = hints.get("wid", -1)
        active_wid = self._get_active_window()
        if wid != -1 and wid == active_wid:
            return notification_id

        duration = timedelta(milliseconds=expire_timeout)
        if duration < MIN_DURATION:
            duration = MIN_DURATION
        if duration > MAX_DURATION:
            duration = MAX_DURATION

        if not notification_id:
            self._id += 1
            notification_id = self._id

        self._queue.add(Notification(notification_id, summary, body, duration))
        return notification_id

    @dbus.service.method(
        "org.freedesktop.Notifications", in_signature="", out_signature="as"
    )
    def GetCapabilities(self) -> str:
        return "body"

    @dbus.service.signal("org.freedesktop.Notifications", signature="uu")
    def NotificationClosed(self, id_in, reason_in):
        pass

    @dbus.service.method(
        "org.freedesktop.Notifications", in_signature="u", out_signature=""
    )
    def CloseNotification(self, id) -> None:
        pass

    @dbus.service.method(
        "org.freedesktop.Notifications", in_signature="", out_signature="ssss"
    )
    def GetServerInformation(self) -> T.Tuple[str, str, str, str]:
        return ("panel", "https://github.com/rr-/dotfiles", "0.0.0", "1")


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


class NotificationsWidget(Widget):
    delay = 0.5

    def __init__(
        self, app: QtWidgets.QApplication, main_window: QtWidgets.QWidget
    ) -> None:
        super().__init__(app, main_window)

        self._queue = NotificationsQueue()
        self._fetcher = NotificationFetcher(self._queue)

        self._icon_label = QtWidgets.QLabel(main_window)
        self._icon_label.mouseReleaseEvent = self.toggle_enable
        self._area = NotificationsAreaWidget(
            self._icon_label.parent(), self._icon_label
        )
        self._enabled = True

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._icon_label

    @property
    def available(self) -> bool:
        return True

    def toggle_enable(self, _event: QtGui.QMouseEvent) -> None:
        self._enabled = not self._enabled
        self.refresh()
        self.render()

    def _refresh_impl(self) -> None:
        pass

    def _render_impl(self) -> None:
        self._set_icon(
            self._icon_label, "bell-on" if self._enabled else "bell-off"
        )
        notification = self._queue.get()
        if notification and self._enabled:
            widget = NotificationWidget(notification, self._area)
            self._area.layout().addWidget(widget)
            self._area.show()
