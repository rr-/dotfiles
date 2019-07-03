import typing as T
from contextlib import contextmanager

import Xlib
import Xlib.display
from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater
from panel.util import exception_guard


class WindowTitleThread(QtCore.QThread):
    updated = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.running = False

        self._disp = Xlib.display.Display()
        self._root = self._disp.screen().root
        self._root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self._WM_NAME = self._disp.intern_atom("WM_NAME")
        self._NET_WM_NAME = self._disp.intern_atom("_NET_WM_NAME")
        self._NET_WM_DESKTOP = self._disp.intern_atom("_NET_WM_DESKTOP")
        self._NET_ACTIVE_WINDOW = self._disp.intern_atom("_NET_ACTIVE_WINDOW")

        self._last_seen_xid = -1

        win_id, _focus_changed = self._active_window_changed()

    def run(self) -> None:
        self.running = True
        while self.running:
            event = self._disp.next_event()

            with exception_guard():
                if event.type != Xlib.X.PropertyNotify:
                    continue

                if event.atom == self._NET_ACTIVE_WINDOW:
                    win_id, focus_changed = self._active_window_changed()
                    if focus_changed:
                        self._update_window_name(win_id)
                elif event.atom in (self._NET_WM_NAME, self._WM_NAME):
                    self._update_window_name(self._last_seen_xid)

    @contextmanager
    def _window_obj(self, win_id: int) -> T.Iterator[T.Any]:
        ret = None
        if win_id != -1:
            try:
                ret = self._disp.create_resource_object("window", win_id)
            except Xlib.error.XError:
                pass
        yield ret

    def _get_active_window(self) -> int:
        response = self._root.get_full_property(
            self._NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType
        )
        if response:
            return int(response.value[0])
        return -1

    def _active_window_changed(self) -> T.Tuple[int, bool]:
        win_id = self._get_active_window()

        focus_changed = win_id != self._last_seen_xid
        if focus_changed:
            with self._window_obj(self._last_seen_xid) as old_win:
                if old_win:
                    old_win.change_attributes(event_mask=Xlib.X.NoEventMask)

            self._last_seen_xid = win_id
            with self._window_obj(win_id) as new_win:
                if new_win:
                    new_win.change_attributes(
                        event_mask=Xlib.X.PropertyChangeMask
                    )

        return win_id, focus_changed

    def _get_window_name(self, window_obj: T.Any) -> str:
        for atom in (self._NET_WM_NAME, self._WM_NAME):
            window_name = window_obj.get_full_property(atom, 0)
            if window_name and window_name.value:
                return window_name.value.decode()
        return "XID: {}".format(window_obj.id)

    def _update_window_name(self, win_id: int) -> None:
        if not win_id:
            self.updated.emit(None)
        else:
            with self._window_obj(win_id) as window_obj:
                if window_obj:
                    self.updated.emit(self._get_window_name(window_obj))


class WindowTitleUpdater(BaseUpdater):
    updated = QtCore.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._thread = WindowTitleThread(self)

        self.window_title: T.Optional[str] = None

        self._thread.updated.connect(self._on_update)
        self._thread.start()

    def _on_update(self, window_title: str) -> None:
        self.window_title = window_title
        self.updated.emit(window_title)
