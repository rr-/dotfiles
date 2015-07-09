from PyQt4 import QtGui
import re
import subprocess

class Monitor(object):
    LAYOUT_TILED   = 1
    LAYOUT_MONOCLE = 2
    name       = None
    focused    = False
    workspaces = []
    layout     = None
    x          = 0
    y          = 0
    width      = 0
    height     = 0

class Workspace(object):
    name    = None
    rect    = None
    focused = False
    free    = True
    urgent  = False

class WorkspacesProvider(object):
    delay = 0

    @staticmethod
    def get_monitors():
        proc = subprocess.Popen(['bspc', 'query', '-T'], stdout=subprocess.PIPE)
        lines = proc.stdout.read().decode('utf-8').strip().replace("\r", '').split("\n")
        mon_defs = [l.split(' ') for l in lines if not l.startswith("\t") and l != '']
        monitors = []
        for mon_def in mon_defs:
            mon = Monitor()
            mon.name = mon_def[0]
            mon.width, mon.height, mon.x, mon.y = re.split('[x+]', mon_def[1])
            monitors.append(mon)
        return monitors

    def __init__(self, main_window):
        self.main_window = main_window

        self.bspc_process = subprocess.Popen(
            ['bspc', 'control', '--subscribe'], stdout=subprocess.PIPE)
        self.monitors = sorted(self.get_monitors(), key=lambda m: m.x)
        self.refresh_workspaces()

        self.widgets = {}
        for i, monitor in enumerate(self.monitors):
            monitor_widget = main_window[i].left_widget
            monitor_widget.ws_widgets = {}
            monitor_widget.wheelEvent = lambda event, monitor=monitor: self.wheel(event, monitor)
            for j, ws in enumerate(monitor.workspaces):
                ws_widget = QtGui.QPushButton(ws.name)
                ws_widget.setProperty('class', 'workspace')
                ws_widget.mouseReleaseEvent = lambda event, ws=ws: self.click(event, ws)
                monitor_widget.ws_widgets[j] = ws_widget
                monitor_widget.layout().addWidget(ws_widget)
            self.widgets[i] = monitor_widget
        self.render()

    def wheel(self, event, monitor):
        subprocess.call(['bspc', 'monitor', '-f', monitor.name])
        subprocess.call(['bspc', 'desktop', '-f', ['prev', 'next'][event.delta() > 0]])

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
                current_monitor.workspaces = []
                current_monitor.focused = key.isupper()

            elif key in 'oOfFuU':
                workspace = Workspace()
                workspace.name = value
                workspace.focused = key.isupper()
                workspace.free = key in 'fF'
                workspace.urgent = key in 'uU'
                current_monitor.workspaces.append(workspace)

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
        self.main_window.reloadStyleSheet()
