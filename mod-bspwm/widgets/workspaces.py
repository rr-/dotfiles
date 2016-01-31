from PyQt5 import QtWidgets
import re
import json
import subprocess

def run(process):
    proc = subprocess.Popen(process, stdout=subprocess.PIPE)
    return proc.stdout.read().decode('utf8')

class Monitor(object):
    def __init__(self):
        self.name         = None
        self.workspaces   = []
        self.x            = 0
        self.y            = 0
        self.width        = 0
        self.height       = 0

class Workspace(object):
    def __init__(self):
        self.name    = None
        self.rect    = None
        self.focused = False
        self.free    = True
        self.urgent  = False

class WorkspacesProvider(object):
    delay = 0
    monitor_names = None

    @staticmethod
    def get_monitors():
        if WorkspacesProvider.monitor_names is None:
            WorkspacesProvider.monitor_names = (
                [l for l in run(['bspc', 'query', '-M']).splitlines() if l])
        monitors = []
        for monitor_name in WorkspacesProvider.monitor_names:
            monitor_spec = json.loads(run(['bspc', 'query', '-T', '-m', monitor_name]))
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
                workspace.free = desktop_spec['root'] is None
                workspace.urgent = False
                children = [desktop_spec['root']]
                while children:
                    child = children.pop()
                    if child is None:
                        continue
                    children.append(child['firstChild'])
                    children.append(child['secondChild'])
                    if child['client']:
                        if bool(child['client']['urgent']):
                            workspace.urgent = True
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
        self.monitors = self.get_monitors()

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
