import os
import sys
import math
from subprocess import run
import mpd
from PyQt5 import QtCore, QtGui, QtWidgets


class MpdWidget:
    delay = 1

    def __init__(self, main_window):
        self.main_window = main_window
        self.client = mpd.MPDClient()
        self.connected = False
        self.mpd_status = None
        self.current_song = None

        self._status_icon_label = QtWidgets.QLabel()
        self._song_label = QtWidgets.QLabel()
        self._shuffle_icon_label = QtWidgets.QLabel()

        self._play_icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(sys.path[0], 'icons', 'play.svg')))
        self._pause_icon = QtGui.QIcon(QtGui.QPixmap(
            os.path.join(sys.path[0], 'icons', 'pause.svg')))
        self._shuffle_on_icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(sys.path[0], 'icons', 'shuffle-on.svg')))
        self._shuffle_off_icon = QtGui.QIcon(
            QtGui.QPixmap(os.path.join(sys.path[0], 'icons', 'shuffle-off.svg')))

        self._status_icon_label.mouseReleaseEvent = self.play_pause_clicked
        self._song_label.mouseReleaseEvent = self.play_pause_clicked
        self._shuffle_icon_label.mouseReleaseEvent = self.shuffle_clicked
        self._status_icon_label.wheelEvent = self.prev_or_next_track
        self._song_label.wheelEvent = self.prev_or_next_track

        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=4))
        container.layout().addWidget(self._status_icon_label)
        container.layout().addWidget(self._song_label)
        container.layout().addWidget(self._shuffle_icon_label)
        main_window[0].layout().addWidget(container)

    def play_pause_clicked(self, _event):
        run(['mpc', 'toggle'])
        self.refresh()
        self.render()

    def prev_or_next_track(self, event):
        run(['mpc', ['prev', 'next'][event.angleDelta().y() > 0]])
        self.refresh()
        self.render()

    def shuffle_clicked(self, _event):
        run(['mpc', 'random'])
        self.refresh()
        self.render()

    def refresh(self):
        if self.connected:
            try:
                self.mpd_status = self.client.status()
                self.current_song = self.client.currentsong()
            except:
                self.mpd_status = None
                self.current_song = None
                self.connected = False
        else:
            try:
                self.client.connect(host='localhost', port=6600)
                self.connected = True
            except:
                self.connected = False

    def render(self):
        if not self.mpd_status:
            return

        if 'state' in self.mpd_status and self.mpd_status['state'] == 'play':
            self._status_icon_label.setPixmap(
                self._play_icon.pixmap(QtCore.QSize(18, 18)))
        else:
            self._status_icon_label.setPixmap(
                self._pause_icon.pixmap(QtCore.QSize(18, 18)))

        text = ''
        if self.current_song:
            if 'title' not in self.current_song \
                    or not self.current_song['title'].strip():
                text = self.current_song['file']
            else:
                if 'artist' in self.current_song:
                    text = self.current_song['artist'] + ' - '
                text += self.current_song['title']
            if 'elapsed' in self.mpd_status and 'time' in self.current_song:
                text += ' %s / %s' % (
                    self.format_seconds(self.mpd_status['elapsed']),
                    self.format_seconds(self.current_song['time']))
            else:
                text += ' (unknown time remaining)'
        self._song_label.setText(text)

        shuffle = 'random' in self.mpd_status \
            and self.mpd_status['random'] == '1'
        if self._shuffle_icon_label.property('active') != shuffle:
            self._shuffle_icon_label.setProperty('active', shuffle)
            if shuffle:
                self._shuffle_icon_label.setPixmap(
                    self._shuffle_on_icon.pixmap(QtCore.QSize(18, 18)))
            else:
                self._shuffle_icon_label.setPixmap(
                    self._shuffle_off_icon.pixmap(QtCore.QSize(18, 18)))

    def format_seconds(self, seconds):
        seconds = math.floor(float(seconds))
        return '%02d:%02d' % (seconds // 60, seconds % 60)
