from PyQt5 import QtWidgets
import re
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
        proc = subprocess.Popen(['bspc', 'query', '-T'], stdout=subprocess.PIPE)
        lines = proc.stdout.read().decode('utf-8').strip().replace("\r", '').split("\n")
        lines = [line for line in lines if line != '']
        current_monitor = None
        current_workspace = None
        monitors = []
        for line in lines:
            chunks = line.strip("\t").split(" ")
            if not line.startswith("\t"):
                current_monitor = Monitor()
                current_monitor.original_id = len(monitors)
                current_monitor.name = chunks[0]
                current_monitor.width, \
                current_monitor.height, \
                current_monitor.x, \
                current_monitor.y = re.split('[x+]', chunks[1])
                monitors.append(current_monitor)
            if line.startswith("\t") and not line.startswith("\t\t"):
                current_workspace = Workspace()
                current_workspace.name = chunks[0]
                current_workspace.focused = '*' in chunks
                current_monitor.workspaces.append(current_workspace)
            if line.startswith("\t\t"):
                current_workspace.free = False
        monitors.sort(key=lambda m: m.x)
        for i, m in enumerate(monitors):
            m.display_id = i
        return monitors

    def __init__(self, main_window):
        self.main_window = main_window

        self.bspc_process = subprocess.Popen(
            ['bspc', 'control', '--subscribe'], stdout=subprocess.PIPE)
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
