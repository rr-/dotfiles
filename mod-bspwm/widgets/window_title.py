from datetime import datetime, timedelta
from PyQt5 import QtWidgets
from collections import defaultdict
import Xlib
import Xlib.display

from .workspaces import WorkspacesProvider

class WindowTitleProvider(object):
    delay = 0

    def __init__(self, main_window, workspaces_updater):
        self.updater = workspaces_updater
        self.labels = []
        for i in range(len(main_window)):
            label = QtWidgets.QLabel()
            label.setProperty('class', 'wintitle')
            main_window[i].left_widget.layout().addWidget(label)
            self.labels.append(label)
        self.desktop_id_to_window_title = defaultdict(str)

        self.disp = Xlib.display.Display()
        self.root = self.disp.screen().root
        self.NET_WM_NAME = self.disp.intern_atom('_NET_WM_NAME')
        self.NET_WM_DESKTOP = self.disp.intern_atom('_NET_WM_DESKTOP')

        self.desktop_id_to_monitor = {}
        for i, m in enumerate(sorted(self.updater.monitors, key=lambda m:m.original_id)):
            for ws in m.workspaces:
                self.desktop_id_to_monitor[len(self.desktop_id_to_monitor)] = m.display_id

        self.update_titles(self.root)

    def refresh(self):
        event = self.disp.next_event()
        type = getattr(event, 'type', None)
        atom = getattr(event, 'atom', None)

        if atom == self.NET_WM_NAME or type in [Xlib.X.FocusIn, Xlib.X.FocusOut]:
            self.update_titles(self.root)

    def update_titles(self, root_window):
        desktop_id_to_window_title = defaultdict(str)
        windows = [root_window]
        while windows:
            window = windows.pop()
            try:
                window.change_attributes(event_mask=Xlib.X.FocusChangeMask | Xlib.X.PropertyChangeMask)

                result = window.get_full_property(self.NET_WM_DESKTOP, 0)
                desktop_id = result.value[0] if result else None
                if desktop_id is not None:
                    result = window.get_full_property(self.NET_WM_NAME, 0)
                    window_title = result.value if result else ''
                    if isinstance(window_title, bytes):
                        window_title = window_title.decode('utf8')
                    if desktop_id not in desktop_id_to_window_title:
                        desktop_id_to_window_title[desktop_id] = window_title

                for child in window.query_tree().children:
                    windows.append(child)
            except Xlib.error.BadWindow:
                pass

        if self.desktop_id_to_window_title != desktop_id_to_window_title:
            self.desktop_id_to_window_title = desktop_id_to_window_title

    def render(self):
        for i, monitor in enumerate(self.updater.monitors):
            focused_desktops = [ws for ws in monitor.workspaces if ws.focused]
            if not focused_desktops:
                continue
            focused_desktop_title = focused_desktops[0].original_id
            self.labels[i].setText(self.desktop_id_to_window_title[focused_desktop_title] or '')
