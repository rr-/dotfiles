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
from panel.widgets.music import MpdWidget
from panel.widgets.stretch import StretchWidget


class MainWindow(QtWidgets.QMainWindow):
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, monitors):
        super().__init__()
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
        QMainWindow {{
            background: #CCC;
        }}
        QWidget {{
            color: #333;
            font-family: 'DejaVu Sans';
            font-weight: 500;
            font-size: 12px;
        }}
        [class=left] QWidget {{
            margin: 1px 3px 3px 0;
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
            background: #EEE;
            height: 10px;
            width: 10px;
            margin: 4px 4px 4px 0;
            padding: 0;
            color: transparent;
            border: 1px solid #888;
        }}
        QWidget[class=workspace][ws_free=False] {{
            background: #AAA;
            border: 1px solid #888;
        }}
        QWidget[class=workspace][ws_focused=True][ws_free=True] {{
            border: 1px solid #6AB;
            background: #8EF;
        }}
        QWidget[class=workspace][ws_focused=True][ws_free=False] {{
            border: 1px solid #378;
            background: #0BC;
        }}
        QWidget[class=workspace][ws_urgent=True] {{
            background: #FFA000;
            border: 1px solid #DD4000;
        }}
        '''.format(content_margin=content_margin))

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
        MpdWidget(app, main_window),
        NetworkUsageWidget(app, main_window),
        BatteryWidget(app, main_window),
        CpuWidget(app, main_window),
        VolumeWidget(app, main_window),
        TimeWidget(app, main_window)
    ]

    def worker(widget, trigger):
        while True:
            widget.refresh()
            if widget.delay > 0:
                time.sleep(widget.delay)
            trigger.emit(widget.render)

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

        t = threading.Thread(
            target=worker, args=(widget, main_window.trigger), daemon=True)
        t.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()


if __name__ == '__main__':
    main()
