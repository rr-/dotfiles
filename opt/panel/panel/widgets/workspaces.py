import json
import subprocess
from PyQt5 import QtWidgets
from panel.widgets.widget import Widget


def run(process):
    proc = subprocess.Popen(process, stdout=subprocess.PIPE)
    return proc.stdout.read().decode('utf8')


class Monitor:
    def __init__(self):
        self.original_id = None
        self.name = None
        self.workspaces = []
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0


class Workspace:
    def __init__(self):
        self.original_id = None
        self.name = None
        self.rect = None
        self.focused = False
        self.free = True
        self.urgent = False


class WorkspacesUpdater:
    monitor_names = None

    def __init__(self):
        self.update()

    def update(self):
        if WorkspacesUpdater.monitor_names is None:
            WorkspacesUpdater.monitor_names = (
                [l for l in run(['bspc', 'query', '-M']).splitlines() if l])
        monitors = []
        workspace_id = 0
        for monitor_name in WorkspacesUpdater.monitor_names:
            monitor_spec = json.loads(
                run(['bspc', 'query', '-T', '-m', monitor_name]))
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
                workspace.focused = \
                    desktop_spec['id'] == monitor_spec['focusedDesktopId']
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
            monitors.append(monitor)
        monitors.sort(key=lambda m: m.x)
        for i, monitor in enumerate(monitors):
            monitor.display_id = i
        self.monitors = monitors


class WorkspacesWidget(Widget):
    delay = 0

    def __init__(self, app, main_window, workspaces_updater):
        super().__init__(app, main_window)
        self._main_window = main_window
        self._updater = workspaces_updater

        self._bspc_process = subprocess.Popen(
            ['bspc', 'subscribe'], stdout=subprocess.PIPE)

        self._container = QtWidgets.QWidget(
            main_window, objectName='workspaces')

        self._container.wheelEvent = self._wheel
        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=0)

        for i, monitor in enumerate(self._updater.monitors):
            for j, workspace in enumerate(monitor.workspaces):
                workspace_widget = QtWidgets.QPushButton(
                    workspace.name, self._container)
                workspace_widget.setProperty('class', 'workspace')
                workspace_widget.setProperty('monitor', i)
                workspace_widget.setProperty('workspace', j)
                workspace_widget.mousePressEvent = self._click
                layout.addWidget(workspace_widget)

    @property
    def container(self):
        return self._container

    @property
    def _workspace_widgets(self):
        for i in range(self._container.layout().count()):
            yield self._container.layout().itemAt(i).widget()

    def _widget_to_workspace(self, widget):
        monitor_idx = widget.property('monitor')
        workspace_idx = widget.property('workspace')
        return self._updater.monitors[monitor_idx].workspaces[workspace_idx]

    def _wheel(self, event):
        with self.exception_guard():
            workspace_widgets = list(self._workspace_widgets)
            focused_widget_idx = None
            for i, workspace_widget in enumerate(workspace_widgets):
                workspace = self._widget_to_workspace(workspace_widget)
                if workspace.focused:
                    focused_widget_idx = i
                    break

            focused_widget_idx += 1 if event.angleDelta().y() > 0 else -1
            focused_widget_idx %= len(workspace_widgets)
            focused_workspace = self._widget_to_workspace(
                workspace_widgets[focused_widget_idx])
            subprocess.call(['bspc', 'desktop', '-f', focused_workspace.name])

    def _click(self, event):
        workspace_widget = self._container.window().childAt(event.globalPos())
        workspace = self._widget_to_workspace(workspace_widget)
        with self.exception_guard():
            subprocess.call(['bspc', 'desktop', '-f', workspace.name])

    def _refresh_impl(self):
        self._bspc_process.stdout.readline().decode('utf8').strip()
        self._updater.update()

    def _render_impl(self):
        for workspace_widget in self._workspace_widgets:
            workspace = self._widget_to_workspace(workspace_widget)
            workspace_widget.setProperty('ws_free', '%s' % workspace.free)
            workspace_widget.setProperty('ws_urgent', '%s' % workspace.urgent)
            workspace_widget.setProperty(
                'ws_focused', '%s' % workspace.focused)
        self._main_window.reload_style_sheet()
