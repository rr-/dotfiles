from contextlib import contextmanager
from PyQt5 import QtCore, QtGui, QtWidgets
import Xlib
import Xlib.display
from panel.widgets.widget import Widget


class WindowTitleWidget(Widget):
    delay = 0

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self._label = QtWidgets.QLabel(main_window)
        self._label.setProperty('class', 'wintitle')

        self._max_width = main_window.width() * 0.8
        self._font_metrics = QtGui.QFontMetrics(self._label.font())

        self._disp = Xlib.display.Display()
        self._root = self._disp.screen().root
        self._root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self._WM_NAME = self._disp.intern_atom('WM_NAME')
        self._NET_WM_NAME = self._disp.intern_atom('_NET_WM_NAME')
        self._NET_WM_DESKTOP = self._disp.intern_atom('_NET_WM_DESKTOP')
        self._NET_ACTIVE_WINDOW = self._disp.intern_atom('_NET_ACTIVE_WINDOW')

        self._last_seen = {'xid': None, 'title': None}

        win_id, _focus_changed = self._active_window_changed()
        self._update_window_name(win_id)
        self._render_impl()

    @property
    def container(self):
        return self._label

    def _refresh_impl(self):
        event = self._disp.next_event()
        if event.type != Xlib.X.PropertyNotify:
            return

        if event.atom == self._NET_ACTIVE_WINDOW:
            win_id, focus_changed = self._active_window_changed()
            if focus_changed:
                self._update_window_name(win_id)
        elif event.atom in (self._NET_WM_NAME, self._WM_NAME):
            self._update_window_name(self._last_seen['xid'])

    def _render_impl(self):
        self._label.setText(
            self._font_metrics.elidedText(
                self._last_seen['title'] or '-',
                QtCore.Qt.ElideRight,
                self._max_width))

    @contextmanager
    def _window_obj(self, win_id):
        ret = None
        if win_id:
            try:
                ret = self._disp.create_resource_object('window', win_id)
            except Xlib.error.XError:
                pass
        yield ret

    def _get_active_window(self):
        response = self._root.get_full_property(
            self._NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType)
        if response:
            return response.value[0]
        return None

    def _active_window_changed(self):
        win_id = self._get_active_window()

        focus_changed = win_id != self._last_seen['xid']
        if focus_changed:
            with self._window_obj(self._last_seen['xid']) as old_win:
                if old_win:
                    old_win.change_attributes(event_mask=Xlib.X.NoEventMask)

            self._last_seen['xid'] = win_id
            with self._window_obj(win_id) as new_win:
                if new_win:
                    new_win.change_attributes(
                        event_mask=Xlib.X.PropertyChangeMask)

        return win_id, focus_changed

    def _get_window_name(self, window_obj):
        for atom in (self._NET_WM_NAME, self._WM_NAME):
            window_name = window_obj.get_full_property(atom, 0)
            return (window_name.value or b'').decode()
        return 'XID: {}'.format(window_obj.id)

    def _update_window_name(self, win_id):
        if not win_id:
            self._last_seen['title'] = '<no window id>'
            return self._last_seen['title']

        with self._window_obj(win_id) as window_obj:
            if window_obj:
                win_title = self._get_window_name(window_obj)
                self._last_seen['title'] = win_title
