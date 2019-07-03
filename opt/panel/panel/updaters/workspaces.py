import json
import subprocess
import typing as T
from dataclasses import dataclass

from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater


@dataclass
class Workspace:
    name: T.Optional[str]
    is_focused: bool
    is_free: bool
    is_urgent: bool


@dataclass
class Monitor:
    name: T.Optional[str]
    workspaces: T.List[Workspace]
    x: int
    y: int
    width: int
    height: int


class WorkspacesThread(QtCore.QThread):
    updated = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.monitor_names: T.List[str] = []
        self.running = False

    def run(self) -> None:
        self.running = True
        self._bspc_process = subprocess.Popen(
            ["bspc", "subscribe"], stdout=subprocess.PIPE
        )

        while self.running:
            # a new line means some changes to windows
            self._bspc_process.stdout.readline().decode().strip()

            monitors = list(self.get_monitors())
            self.updated.emit(monitors)

    def get_monitors(self) -> T.Iterable[Monitor]:
        if not self.monitor_names:
            self.monitor_names = self._get_monitor_names()

        monitors: T.List[Monitor] = []
        workspace_id = 0
        for monitor_name in self.monitor_names:
            monitor_spec = self._get_monitor_spec(monitor_name)

            monitor = Monitor(
                name=monitor_name,
                workspaces=[],
                x=int(monitor_spec["rectangle"]["x"]),
                y=int(monitor_spec["rectangle"]["y"]),
                width=int(monitor_spec["rectangle"]["width"]),
                height=int(monitor_spec["rectangle"]["height"]),
            )

            for desktop_spec in monitor_spec["desktops"]:
                workspace = Workspace(
                    name=desktop_spec["name"],
                    is_focused=(
                        desktop_spec["id"] == monitor_spec["focusedDesktopId"]
                    ),
                    is_free=desktop_spec["root"] is None,
                    is_urgent=False,
                )

                workspace_id += 1
                children = [desktop_spec["root"]]
                while children:
                    child = children.pop()
                    if child is None:
                        continue
                    children.append(child["firstChild"])
                    children.append(child["secondChild"])
                    if child["client"]:
                        if bool(child["client"]["urgent"]):
                            workspace.is_urgent = True
                monitor.workspaces.append(workspace)
            monitors.append(monitor)

        return sorted(monitors, key=lambda monitor: monitor.x)

    def _get_monitor_names(self) -> T.List[str]:
        return [
            line
            for line in subprocess.run(
                ["bspc", "query", "-M"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            if line
        ]

    def _get_monitor_spec(self, monitor_name: str) -> T.Any:
        return json.loads(
            subprocess.run(
                ["bspc", "query", "-T", "-m", monitor_name],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )


class WorkspacesUpdater(BaseUpdater):
    updated = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._thread = WorkspacesThread(self)

        self.monitors = self._thread.get_monitors()

        self._thread.updated.connect(self._on_update)
        self._thread.start()

    def _on_update(self, monitors: T.List[Monitor]) -> None:
        self.monitors = monitors
        self.updated.emit()
