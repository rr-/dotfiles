import json
import subprocess
import typing as T

from PyQt5 import QtGui, QtWidgets

from panel.util import run
from panel.widgets.widget import Widget


class Workspace:
    def __init__(self) -> None:
        self.name: T.Optional[str] = None
        self.focused = False
        self.free = True
        self.urgent = False


class Monitor:
    def __init__(self) -> None:
        self.name: T.Optional[str] = None
        self.workspaces: T.List[Workspace] = []
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0


class WorkspacesUpdater:
    monitor_names: T.List[str] = []

    def __init__(self) -> None:
        self.update()

    def update(self) -> None:
        if not WorkspacesUpdater.monitor_names:
            WorkspacesUpdater.monitor_names = [
                line
                for line in run(['bspc', 'query', '-M']).stdout.splitlines()
                if line
            ]

        monitors: T.List[Monitor] = []
        workspace_id = 0
        for monitor_name in WorkspacesUpdater.monitor_names:
            monitor_spec = json.loads(
                run(['bspc', 'query', '-T', '-m', monitor_name]).stdout
            )
            monitor = Monitor()
            monitor.name = monitor_name
            monitor.width = int(monitor_spec['rectangle']['width'])
            monitor.height = int(monitor_spec['rectangle']['height'])
            monitor.x = int(monitor_spec['rectangle']['x'])
            monitor.y = int(monitor_spec['rectangle']['y'])
            for desktop_spec in monitor_spec['desktops']:
                workspace = Workspace()
                workspace.name = desktop_spec['name']
                workspace.focused = (
                    desktop_spec['id'] == monitor_spec['focusedDesktopId']
                )
                workspace.free = desktop_spec['root'] is None
                workspace.urgent = False
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
        self.monitors = monitors


class WorkspacesWidget(Widget):
    delay = 0

    def __init__(
            self,
            app: QtWidgets.QApplication,
            main_window: QtWidgets.QWidget,
            workspaces_updater: WorkspacesUpdater,
    ) -> None:
        super().__init__(app, main_window)
        self._main_window = main_window
        self._updater = workspaces_updater

        self._bspc_process = subprocess.Popen(
            ['bspc', 'subscribe'], stdout=subprocess.PIPE
        )

        self._container = QtWidgets.QWidget(
            main_window, objectName='workspaces'
        )

        self._container.wheelEvent = self._wheel
        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=0)

        for i, monitor in enumerate(self._updater.monitors):
            for j, workspace in enumerate(monitor.workspaces):
                workspace_widget = QtWidgets.QPushButton(
                    workspace.name, self._container
                )
                workspace_widget.setProperty('class', 'workspace')
                workspace_widget.setProperty('monitor', i)
                workspace_widget.setProperty('workspace', j)
                workspace_widget.mousePressEvent = self._click
                layout.addWidget(workspace_widget)

    @property
    def container(self) -> QtWidgets.QWidget:
        return self._container

    @property
    def _workspace_widgets(self) -> T.Iterable[QtWidgets.QWidget]:
        for i in range(self._container.layout().count()):
            yield self._container.layout().itemAt(i).widget()

    def _widget_to_workspace(self, widget: QtWidgets.QWidget) -> Workspace:
        monitor_idx = widget.property('monitor')
        workspace_idx = widget.property('workspace')
        return self._updater.monitors[monitor_idx].workspaces[workspace_idx]

    def _wheel(self, event: QtGui.QWheelEvent) -> None:
        with self.exception_guard():
            workspace_widgets = list(self._workspace_widgets)
            focused_widget_idx = None
            for i, workspace_widget in enumerate(workspace_widgets):
                workspace = self._widget_to_workspace(workspace_widget)
                if workspace.focused:
                    focused_widget_idx = i
                    break
            if focused_widget_idx is None:
                return

            focused_widget_idx += 1 if event.angleDelta().y() > 0 else -1
            focused_widget_idx %= len(workspace_widgets)
            focused_workspace = self._widget_to_workspace(
                workspace_widgets[focused_widget_idx]
            )
            run(['bspc', 'desktop', '-f', focused_workspace.name or '?'])

    def _click(self, event: QtGui.QMouseEvent) -> None:
        workspace_widget = self._container.window().childAt(event.globalPos())
        workspace = self._widget_to_workspace(workspace_widget)
        with self.exception_guard():
            run(['bspc', 'desktop', '-f', workspace.name or '?'])

    def _refresh_impl(self) -> None:
        self._bspc_process.stdout.readline().decode().strip()
        self._updater.update()

    def _render_impl(self) -> None:
        for workspace_widget in self._workspace_widgets:
            workspace = self._widget_to_workspace(workspace_widget)
            workspace_widget.setProperty('ws_free', '%s' % workspace.free)
            workspace_widget.setProperty('ws_urgent', '%s' % workspace.urgent)
            workspace_widget.setProperty(
                'ws_focused', str(workspace.focused)
            )
        self._main_window.reload_style_sheet()
