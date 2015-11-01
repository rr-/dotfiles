from datetime import datetime, timedelta
from PyQt5 import QtWidgets
import Xlib
import Xlib.display

from .workspaces import WorkspacesProvider

class WindowTitleProvider(object):
    delay = 0

    def __init__(self, main_window):
        self.changed = False
        self.labels = []
        self.window_names = []
        for i in range(len(main_window)):
            label = QtWidgets.QLabel()
            label.setProperty('class', 'wintitle')
            main_window[i].left_widget.layout().addWidget(label)
            self.labels.append(label)
            self.window_names.append(None)

        WorkspacesProvider.window_title_provider = self

        self.disp = Xlib.display.Display()
        self.root = self.disp.screen().root
        self.NET_WM_NAME = self.disp.intern_atom('_NET_WM_NAME')
        self.NET_WM_DESKTOP = self.disp.intern_atom('_NET_WM_DESKTOP')
        self.NET_ACTIVE_WINDOW = self.disp.intern_atom('_NET_ACTIVE_WINDOW')

        self.desktop_to_monitor = {}
        monitors = WorkspacesProvider.get_monitors()
        for i, m in enumerate(sorted(monitors, key=lambda m:m.original_id)):
            for ws in m.workspaces:
                self.desktop_to_monitor[len(self.desktop_to_monitor)] = m.display_id

        for window in self.root.query_tree().children:
            self.attach_event_handler(window)
        self.attach_event_handler(self.root)

        self.update_title_for_all_windows()

    def refresh(self):
        event = self.disp.next_event()
        type = getattr(event, 'type', None)
        atom = getattr(event, 'atom', None)

        #transient_for = window.get_wm_transient_for()
        #attrs = window.get_attributes()
        #if attrs.map_state != Xlib.X.IsViewable:
        #    return

        if atom == self.NET_WM_NAME or type == Xlib.X.FocusOut or type == Xlib.X.FocusIn:
            window = self.get_active_window()
            self.update_title_for_window(window)
            self.attach_event_handler(window)
            self.changed = True

    def attach_event_handler(self, window):
        window.change_attributes(event_mask=Xlib.X.FocusChangeMask | Xlib.X.PropertyChangeMask)

    def update_title_for_all_windows(self, root_window=None):
        for window in self.root.query_tree().children:
            self.update_title_for_window(window)

    def get_active_window(self):
        window_id = self.root.get_full_property(
            self.NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        return self.disp.create_resource_object('window', window_id)

    def get_monitor_id_for_window(self, window):
        try:
            result = window.get_full_property(self.NET_WM_DESKTOP, 0)
        except Xlib.error.BadWindow:
            return None
        if result is None:
            return None
        desktop_id = result.value[0]
        if desktop_id > len(self.desktop_to_monitor):
            return None
        return self.desktop_to_monitor[desktop_id]

    def reset_title_for_window(self, window):
        monitor_id = self.get_monitor_id_for_window(window)
        if monitor_id is not None:
            self.window_names[monitor_id] = ''

    def update_title_for_window(self, window):
        monitor_id = self.get_monitor_id_for_window(window)
        if monitor_id is not None:
            try:
                result = window.get_full_property(self.NET_WM_NAME, 0)
            except Xlib.error.BadWindow:
                result = None

            if result:
                self.window_names[monitor_id] = result.value
            else:
                self.window_names[monitor_id] = ''

    def render(self):
        if self.changed:
            for i, label in enumerate(self.labels):
                window_name = self.window_names[i]
                if isinstance(window_name, bytes):
                    window_name = window_name.decode('utf8')
                label.setText(window_name or '')
            self.changed = False
