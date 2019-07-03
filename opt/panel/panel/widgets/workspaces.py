import typing as T
from subprocess import run

from PyQt5 import QtGui, QtWidgets

from panel.updaters.workspaces import Workspace, WorkspacesUpdater
from panel.util import exception_guard


class WorkspacesWidget(QtWidgets.QWidget):
    def __init__(
        self, workspaces_updater: WorkspacesUpdater, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent, objectName="workspaces")
        self._updater = workspaces_updater

        self.wheelEvent = self._wheel
        layout = QtWidgets.QHBoxLayout(self, margin=0, spacing=0)

        for i, monitor in enumerate(self._updater.monitors):
            for j, workspace in enumerate(monitor.workspaces):
                workspace_widget = QtWidgets.QPushButton(workspace.name, self)
                workspace_widget.setProperty("class", "workspace")
                workspace_widget.setProperty("monitor", i)
                workspace_widget.setProperty("workspace", j)
                workspace_widget.mousePressEvent = self._click
                layout.addWidget(workspace_widget)

        self._updater.updated.connect(self._on_update)

    @property
    def _workspace_widgets(self) -> T.Iterable[QtWidgets.QWidget]:
        for i in range(self.layout().count()):
            yield self.layout().itemAt(i).widget()

    def _widget_to_workspace(self, widget: QtWidgets.QWidget) -> Workspace:
        monitor_idx = widget.property("monitor")
        workspace_idx = widget.property("workspace")
        return self._updater.monitors[monitor_idx].workspaces[workspace_idx]

    def _wheel(self, event: QtGui.QWheelEvent) -> None:
        with exception_guard():
            workspace_widgets = list(self._workspace_widgets)
            focused_widget_idx = None
            for i, workspace_widget in enumerate(workspace_widgets):
                workspace = self._widget_to_workspace(workspace_widget)
                if workspace.is_focused:
                    focused_widget_idx = i
                    break
            if focused_widget_idx is None:
                return

            focused_widget_idx += 1 if event.angleDelta().y() > 0 else -1
            focused_widget_idx %= len(workspace_widgets)
            focused_workspace = self._widget_to_workspace(
                workspace_widgets[focused_widget_idx]
            )
            run(
                ["bspc", "desktop", "-f", focused_workspace.name or "?"],
                check=True,
            )

    def _click(self, event: QtGui.QMouseEvent) -> None:
        workspace_widget = self.window().childAt(event.globalPos())
        workspace = self._widget_to_workspace(workspace_widget)
        with exception_guard():
            run(["bspc", "desktop", "-f", workspace.name or "?"], check=True)

    def _on_update(self) -> None:
        for workspace_widget in self._workspace_widgets:
            workspace = self._widget_to_workspace(workspace_widget)
            workspace_widget.setProperty("ws_free", str(workspace.is_free))
            workspace_widget.setProperty("ws_urgent", str(workspace.is_urgent))
            workspace_widget.setProperty(
                "ws_focused", str(workspace.is_focused)
            )

            # recalculate stylesheet for this widget
            workspace_widget.setStyleSheet("/**/")
            workspace_widget.setStyleSheet("")
