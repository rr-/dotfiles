from PyQt5 import QtWidgets
import re
import json
import subprocess

class Monitor(object):
    LAYOUT_TILED   = 1
    LAYOUT_MONOCLE = 2

    def __init__(self):
        self.name       = None
        self.focused    = False
        self.workspaces = []
        self.layout     = None
        self.x          = 0
        self.y          = 0
        self.width      = 0
        self.height     = 0

class Workspace(object):
    def __init__(self):
        self.name    = None
        self.rect    = None
        self.focused = False
        self.free    = True
        self.urgent  = False

class WorkspacesProvider(object):
    delay = 0
    window_title_provider = None

    @staticmethod
    def get_monitors():
        proc = subprocess.Popen(['bspc', 'query', '-M'], stdout=subprocess.PIPE)
        monitor_names = [l for l in proc.stdout.read().decode('utf8').splitlines() if l]
        monitors = []
        for monitor_name in monitor_names:
            proc = subprocess.Popen(['bspc', 'query', '-T', '-m', monitor_name], stdout=subprocess.PIPE)
            monitor_spec = json.loads(proc.stdout.read().decode('utf8'))
            monitor = Monitor()
            monitor.original_id = len(monitors)
            monitor.name = monitor_name
            monitor.width = int(monitor_spec['rectangle']['width'])
            monitor.height = int(monitor_spec['rectangle']['height'])
            monitor.x = int(monitor_spec['rectangle']['x'])
            monitor.y = int(monitor_spec['rectangle']['y'])
            for desktop_spec in monitor_spec['desktops']:
                workspace = Workspace()
                workspace.name = desktop_spec['name']
                workspace.focused = workspace.name == monitor_spec['focusedDesktopName']
                workspace.free = desktop_spec['root'] is not None
                monitor.workspaces.append(workspace)
            monitors.append(monitor)
        monitors.sort(key=lambda m: m.x)
        for i, m in enumerate(monitors):
            m.display_id = i
        return monitors

    def __init__(self, main_window):
        self.main_window = main_window

        self.bspc_process = subprocess.Popen(
            ['bspc', 'subscribe'], stdout=subprocess.PIPE)
        self.monitors = self.get_monitors()
        self.refresh_workspaces()

        self.widgets = {}
        for i, monitor in enumerate(self.monitors):
            monitor_widget = main_window[i].left_widget
            monitor_widget.ws_widgets = {}
            monitor_widget.wheelEvent = lambda event, monitor=monitor: self.wheel(event, monitor)
            for j, ws in enumerate(monitor.workspaces):
                ws_widget = QtWidgets.QPushButton(ws.name)
                ws_widget.setProperty('class', 'workspace')
                ws_widget.mouseReleaseEvent = lambda event, ws=ws: self.click(event, ws)
                monitor_widget.ws_widgets[j] = ws_widget
                monitor_widget.layout().addWidget(ws_widget)
            self.widgets[i] = monitor_widget
        self.render()

    def wheel(self, event, monitor):
        subprocess.call(['bspc', 'monitor', '-f', monitor.name])
        subprocess.call(['bspc', 'desktop', '-f', ['prev', 'next'][event.angleDelta().y() > 0]])

    def click(self, event, ws):
        subprocess.call(['bspc', 'desktop', '-f', ws.name])

    def refresh_workspaces(self):
        line = self.bspc_process.stdout.readline().decode('utf8').strip()
        line = re.sub('^W', '', line)
        if line == '':
            return

        for item in line.split(':'):
            key, value = item[0], item[1:]

            if key in 'mM':
                chosen_monitor = [m for m in self.monitors if m.name == value]
                current_monitor = chosen_monitor[0]
                current_monitor.focused = key.isupper()

            elif key in 'oOfFuU':
                workspace = [w for w in current_monitor.workspaces if w.name == value][0]
                workspace.focused = key.isupper()
                workspace.free = key in 'fF'
                workspace.urgent = key in 'uU'

            elif key in 'lL':
                if value in 'mM':
                    current_monitor.layout = Monitor.LAYOUT_MONOCLE
                elif value in 'tT':
                    current_monitor.layout = Monitor.LAYOUT_TILED

    def refresh(self):
        self.refresh_workspaces()

    def render(self):
        for i, monitor in enumerate(self.monitors):
            for j, ws in enumerate(monitor.workspaces):
                self.widgets[i].ws_widgets[j].setProperty('ws_focused', '%s' % ws.focused)
                self.widgets[i].ws_widgets[j].setProperty('ws_urgent', '%s' % ws.urgent)
                self.widgets[i].ws_widgets[j].setProperty('ws_free', '%s' % ws.free)
                if ws.focused and ws.free and WorkspacesProvider.window_title_provider is not None:
                    WorkspacesProvider.window_title_provider.labels[monitor.display_id].setText('')
                    WorkspacesProvider.window_title_provider.window_names[monitor.display_id] = ''
        self.main_window.reloadStyleSheet()
