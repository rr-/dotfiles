import json
import subprocess
from PyQt5 import QtWidgets

def run(process):
    proc = subprocess.Popen(process, stdout=subprocess.PIPE)
    return proc.stdout.read().decode('utf8')

class Monitor(object):
    def __init__(self):
        self.original_id = None
        self.name = None
        self.workspaces = []
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

class Workspace(object):
    def __init__(self):
        self.original_id = None
        self.name = None
        self.rect = None
        self.focused = False
        self.free = True
        self.urgent = False

class WorkspacesUpdater(object):
    monitor_names = None

    def __init__(self):
        self.update()

    def update(self):
        if WorkspacesUpdater.monitor_names is None:
            WorkspacesUpdater.monitor_names = (
                [l for l in run(['bspc', 'query', '-M']).splitlines() if l])
        self.monitors = []
        workspace_id = 0
        for monitor_name in WorkspacesUpdater.monitor_names:
            monitor_spec = json.loads(run(['bspc', 'query', '-T', '-m', monitor_name]))
            monitor = Monitor()
            monitor.original_id = len(self.monitors)
            monitor.name = monitor_name
            monitor.width = int(monitor_spec['rectangle']['width'])
            monitor.height = int(monitor_spec['rectangle']['height'])
            monitor.x = int(monitor_spec['rectangle']['x'])
            monitor.y = int(monitor_spec['rectangle']['y'])
            for desktop_spec in monitor_spec['desktops']:
                workspace = Workspace()
                workspace.name = desktop_spec['name']
                workspace.focused = desktop_spec['id'] == monitor_spec['focusedDesktopId']
                workspace.free = desktop_spec['root'] is None
                workspace.urgent = False
                workspace.original_id = workspace_id
                workspace_id += 1
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
            self.monitors.append(monitor)
        self.monitors.sort(key=lambda m: m.x)
        for i, m in enumerate(self.monitors):
            m.display_id = i

class WorkspacesProvider(object):
    delay = 0

    def __init__(self, main_window, workspaces_updater):
        self._main_window = main_window
        self._updater = workspaces_updater

        self._bspc_process = subprocess.Popen(
            ['bspc', 'subscribe'], stdout=subprocess.PIPE)

        self._widgets = {}
        for i, monitor in enumerate(self._updater.monitors):
            monitor_widget = main_window[i].left_widget
            monitor_widget.ws_widgets = {}
            monitor_widget.wheelEvent = lambda event, monitor=monitor: self.wheel(event, monitor)
            for j, ws in enumerate(monitor.workspaces):
                ws_widget = QtWidgets.QPushButton(ws.name)
                ws_widget.setProperty('class', 'workspace')
                ws_widget.mouseReleaseEvent = lambda event, ws=ws: self.click(event, ws)
                monitor_widget.ws_widgets[j] = ws_widget
                monitor_widget.layout().addWidget(ws_widget)
            self._widgets[i] = monitor_widget
        self.render()

    def wheel(self, event, monitor):
        subprocess.call(['bspc', 'monitor', '-f', monitor.name])
        subprocess.call(['bspc', 'desktop', '-f', ['prev', 'next'][event.angleDelta().y() > 0]])

    def click(self, event, ws):
        subprocess.call(['bspc', 'desktop', '-f', ws.name])

    def refresh(self):
        line = self._bspc_process.stdout.readline().decode('utf8').strip()
        self._updater.update()

    def render(self):
        for i, monitor in enumerate(self._updater.monitors):
            for j, ws in enumerate(monitor.workspaces):
                self._widgets[i].ws_widgets[j].setProperty('ws_focused', '%s' % ws.focused)
                self._widgets[i].ws_widgets[j].setProperty('ws_urgent', '%s' % ws.urgent)
                self._widgets[i].ws_widgets[j].setProperty('ws_free', '%s' % ws.free)
        self._main_window.reloadStyleSheet()
