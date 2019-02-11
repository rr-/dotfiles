#!/usr/bin/env python3
import os
import signal
import sys
import threading
import time
import typing as T

import dbus.mainloop.pyqt5
from PyQt5 import QtCore, QtWidgets

from panel import settings
from panel.colors import Colors
from panel.util import run
from panel.widgets.battery import BatteryWidget
from panel.widgets.cpu import CpuWidget
from panel.widgets.mpvmd import MpvmdWidget
from panel.widgets.net import NetworkUsageWidget
from panel.widgets.notifications import NotificationsWidget
from panel.widgets.stretch import StretchWidget
from panel.widgets.time import TimeWidget
from panel.widgets.volume import VolumeWidget
from panel.widgets.window_title import WindowTitleWidget
from panel.widgets.workspaces import (
    Monitor,
    WorkspacesUpdater,
    WorkspacesWidget,
)

STYLESHEET_TEMPLATE = """
#central {{
    background: {colors.background};
}}
QWidget {{
    color: {colors.foreground};
    font-family: 'DejaVu Sans';
    font-weight: 500;
    font-size: 12px;
}}
QWidget[class=workspace] {{
    height: 20px;
    width: 20px;
    margin: 0 3px 0 0;
    padding: 0;
    background: {colors.workspace_background};
    color: {colors.workspace_foreground};
    border: 0;
}}
QWidget[class=workspace][ws_free=False] {{
    background: {colors.workspace_full_background};
    color: {colors.workspace_full_foreground};
}}
QWidget[class=workspace][ws_focused=True][ws_free=True] {{
    background: {colors.workspace_focused_background};
    color: {colors.workspace_focused_foreground};
}}
QWidget[class=workspace][ws_focused=True][ws_free=False] {{
    background: {colors.workspace_focused_full_background};
    color: {colors.workspace_focused_full_foreground};
}}
QWidget[class=workspace][ws_urgent=True] {{
    background: {colors.workspace_urgent_background};
    color: {colors.workspace_urgent_foreground};
}}
QWidget[class=chart] {{
    height: 16px;
    margin: 2px;
}}
QDialog {{
    background: {colors.background};
    color: {colors.foreground};
}}
"""


class MainWindow(QtWidgets.QMainWindow):
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, monitors: T.List[Monitor]) -> None:
        super().__init__(flags=QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            QtCore.Qt.SplashScreen
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setFixedSize(
            monitors[0].width / self.devicePixelRatioF(), settings.HEIGHT
        )
        self.move(0, 0)
        self.show()

        window_gap = int(run(["bspc", "config", "window_gap"]).stdout)
        window_border = int(run(["bspc", "config", "border_width"]).stdout)
        content_margin = (
            window_gap + window_border
        ) / self.devicePixelRatioF()

        self.setStyleSheet(STYLESHEET_TEMPLATE.format(colors=Colors))

        central_widget = QtWidgets.QWidget(self, objectName="central")
        layout = QtWidgets.QHBoxLayout(central_widget, margin=0, spacing=12)
        layout.setContentsMargins(content_margin, 0, content_margin, 0)
        self.setCentralWidget(central_widget)
        self.trigger.connect(self.render)

    def render(self, renderer: T.Callable[[], None]) -> None:
        renderer()

    def reload_style_sheet(self) -> None:
        old_stylesheet = self.styleSheet()
        self.setStyleSheet("")
        self.setStyleSheet(old_stylesheet)


def main() -> None:
    dbus.mainloop.pyqt5.DBusQtMainLoop(set_as_default=True)

    app = QtWidgets.QApplication([os.fsencode(arg) for arg in sys.argv])
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    workspaces_updater = WorkspacesUpdater()
    main_window = MainWindow(workspaces_updater.monitors)
    main_window.setWindowTitle("panel")

    widgets = [
        WorkspacesWidget(app, main_window, workspaces_updater),
        WindowTitleWidget(app, main_window),
        StretchWidget(app, main_window),
        MpvmdWidget(app, main_window),
        NetworkUsageWidget(app, main_window),
        BatteryWidget(app, main_window),
        CpuWidget(app, main_window),
        VolumeWidget(app, main_window),
        NotificationsWidget(app, main_window),
        TimeWidget(app, main_window),
    ]

    def worker(widget: QtWidgets.QWidget, trigger: QtCore.pyqtSignal) -> None:
        while True:
            widget.refresh()
            trigger.emit(widget.render)
            if widget.delay > 0:
                time.sleep(widget.delay)

    physical_height = main_window.height() * app.devicePixelRatio()
    for monitor in workspaces_updater.monitors:
        run(
            [
                "bspc",
                "config",
                "-m",
                monitor.name or "?",
                "top_padding",
                str(physical_height),
            ]
        )

    for widget in widgets:
        if not widget.available:
            print(f"{widget.__class__} is not available on this system")
            continue
        main_window.centralWidget().layout().addWidget(widget.container)
        thread = threading.Thread(
            target=worker, args=(widget, main_window.trigger), daemon=True
        )
        thread.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()


if __name__ == "__main__":
    main()
