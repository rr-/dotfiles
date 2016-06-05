from collections import defaultdict
from PyQt5 import QtWidgets
import Xlib
import Xlib.display

class WindowTitleProvider(object):
    delay = 0

    def __init__(self, main_window, workspaces_updater):
        self._updater = workspaces_updater
        self._labels = []
        for i, _ in enumerate(main_window):
            label = QtWidgets.QLabel()
            label.setProperty('class', 'wintitle')
            main_window[i].left_widget.layout().addWidget(label)
            self._labels.append(label)
        self._desktop_id_to_window_title = defaultdict(str)

        self._disp = Xlib.display.Display()
        self._root = self._disp.screen().root
        self._NET_WM_NAME = self._disp.intern_atom('_NET_WM_NAME')
        self._NET_WM_DESKTOP = self._disp.intern_atom('_NET_WM_DESKTOP')

        self._desktop_id_to_monitor = {}
        for i, m in enumerate(sorted(self._updater.monitors, key=lambda m: m.original_id)):
            for ws in m.workspaces:
                self._desktop_id_to_monitor[len(self._desktop_id_to_monitor)] = m.display_id

        self._update_titles(self._root)

    def refresh(self):
        event = self._disp.next_event()
        event_type = getattr(event, 'type', None)
        event_atom = getattr(event, 'atom', None)

        if event_atom == self._NET_WM_NAME \
                or event_type in [Xlib.X.FocusIn, Xlib.X.FocusOut]:
            self._update_titles(self._root)

    def render(self):
        for i, monitor in enumerate(self._updater.monitors):
            focused_desktops = [ws for ws in monitor.workspaces if ws.focused]
            if not focused_desktops:
                continue
            focused_desktop_title = focused_desktops[0].original_id
            self._labels[i].setText(
                self._desktop_id_to_window_title[focused_desktop_title] or '')

    def _update_titles(self, root_window):
        desktop_id_to_window_title = defaultdict(str)
        windows = [root_window]
        while windows:
            window = windows.pop()
            try:
                window.change_attributes(
                    event_mask=Xlib.X.FocusChangeMask | Xlib.X.PropertyChangeMask)

                result = window.get_full_property(self._NET_WM_DESKTOP, 0)
                desktop_id = result.value[0] if result else None
                if desktop_id is not None:
                    result = window.get_full_property(self._NET_WM_NAME, 0)
                    window_title = result.value if result else ''
                    if isinstance(window_title, bytes):
                        window_title = window_title.decode('utf8')
                    if desktop_id not in desktop_id_to_window_title:
                        desktop_id_to_window_title[desktop_id] = window_title

                for child in window.query_tree().children:
                    windows.append(child)
            except Xlib.error.BadWindow:
                pass

        if self._desktop_id_to_window_title != desktop_id_to_window_title:
            self._desktop_id_to_window_title = desktop_id_to_window_title
