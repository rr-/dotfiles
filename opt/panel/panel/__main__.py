#!/usr/bin/env python3
import os
import sys
import threading
import time
import signal
from subprocess import run, PIPE
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from panel import settings
from panel.widgets.workspaces import WorkspacesWidget, WorkspacesUpdater
from panel.widgets.window_title import WindowTitleWidget
from panel.widgets.time import TimeWidget
from panel.widgets.volume import VolumeWidget
from panel.widgets.cpu import CpuWidget
from panel.widgets.net import NetworkUsageWidget
from panel.widgets.battery import BatteryWidget
from panel.widgets.mpvmd import MpvmdWidget
from panel.widgets.stretch import StretchWidget
from panel.colors import Colors


class MainWindow(QtWidgets.QMainWindow):
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, monitors):
        super().__init__(flags=QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            QtCore.Qt.SplashScreen
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.X11BypassWindowManagerHint)
        self.setFixedSize(
            sum([int(m.width) for m in monitors]) / self.devicePixelRatioF(),
            settings.HEIGHT)
        self.move(0, 0)
        self.show()

        window_gap = int(
            run(['bspc', 'config', 'window_gap'], stdout=PIPE).stdout)
        window_border = int(
            run(['bspc', 'config', 'border_width'], stdout=PIPE).stdout)
        content_margin = (
            (window_gap + window_border) / self.devicePixelRatioF())

        self.setStyleSheet('''
        QMainWindow QWidget {{
            background: {colors.background};
        }}
        QWidget {{
            color: {colors.foreground};
            font-family: 'DejaVu Sans';
            font-weight: 500;
            font-size: 12px;
        }}
        [class=right] QWidget {{
            margin: 1px 0 3px 3px;
        }}
        #workspaces {{
            padding-left: {content_margin}px;
        }}
        #time {{
            padding-right: {content_margin}px;
        }}
        QWidget[class=workspace] {{
            height: 20px;
            width: 20px;
            margin: 0 3px 0 0;
            padding: 0;
            color: black;
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
            background: orange;
            height: 16px;
            margin: 2px;
            border: 4px solid red;
        }}
        '''.format(content_margin=content_margin, colors=Colors))

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=0))
        self.setCentralWidget(central_widget)

        self.monitor_widgets = []
        for monitor in monitors:
            monitor_widget = QtWidgets.QWidget(size=QtCore.QSize(
                monitor.width / self.devicePixelRatioF(), 0))
            monitor_widget.setLayout(
                QtWidgets.QHBoxLayout(margin=0, spacing=12))
            central_widget.layout().addWidget(monitor_widget)
            self.monitor_widgets.append(monitor_widget)

        self.trigger.connect(self.render)

    def render(self, renderer):
        renderer()

    def reloadStyleSheet(self):
        old_stylesheet = self.styleSheet()
        self.setStyleSheet('')
        self.setStyleSheet(old_stylesheet)

    def __len__(self):
        return len(self.monitor_widgets)

    def __getitem__(self, index):
        return self.monitor_widgets[index]


def main():
    app = QtWidgets.QApplication([os.fsencode(arg) for arg in sys.argv])
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    workspaces_updater = WorkspacesUpdater()
    main_window = MainWindow(workspaces_updater.monitors)
    main_window.setWindowTitle('panel')

    widgets = [
        WorkspacesWidget(app, main_window, workspaces_updater),
        WindowTitleWidget(app, main_window, workspaces_updater),
        StretchWidget(app, main_window),
        MpvmdWidget(app, main_window),
        NetworkUsageWidget(app, main_window),
        BatteryWidget(app, main_window),
        CpuWidget(app, main_window),
        VolumeWidget(app, main_window),
        TimeWidget(app, main_window)
    ]

    def worker(widget, trigger):
        while True:
            widget.refresh()
            trigger.emit(widget.render)
            if widget.delay > 0:
                time.sleep(widget.delay)

    physical_height = main_window.height() * app.devicePixelRatio()
    for monitor in workspaces_updater.monitors:
        run([
            'bspc',
            'config',
            '-m', monitor.name,
            'top_padding', str(physical_height)])

    for widget in widgets:
        widget.refresh()
        main_window.trigger.emit(widget.render)

        thread = threading.Thread(
            target=worker, args=(widget, main_window.trigger), daemon=True)
        thread.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()


if __name__ == '__main__':
    main()
