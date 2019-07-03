import typing as T
from dataclasses import dataclass
from datetime import timedelta

import dbus
import dbus.service
import Xlib
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater

MIN_DURATION = timedelta(milliseconds=5000)
MAX_DURATION = timedelta(milliseconds=10000)


@dataclass
class Notification:
    summary: str
    body: str
    duration: timedelta


class NotificationFetcher(dbus.service.Object):
    def __init__(self, on_notify: T.Callable[[Notification], None]) -> None:
        self._on_notify = on_notify
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

        self._on_notify(Notification(summary, body, duration))
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


class NotificationsUpdater(BaseUpdater):
    notified = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()

        def on_notify(notification: Notification) -> None:
            self.notified.emit(notification)

        self._fetcher = NotificationFetcher(on_notify=on_notify)
