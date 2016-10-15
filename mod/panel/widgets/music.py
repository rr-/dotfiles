import math
from subprocess import run
import mpd
from PyQt5 import QtWidgets
from .util import set_icon


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

        self._status_icon_label.mouseReleaseEvent = self.play_pause_clicked
        self._song_label.mouseReleaseEvent = self.play_pause_clicked
        self._shuffle_icon_label.mouseReleaseEvent = self.shuffle_clicked
        self._status_icon_label.wheelEvent = self.prev_or_next_track
        self._song_label.wheelEvent = self.prev_or_next_track

        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QHBoxLayout(margin=0, spacing=6))
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
        try:
            if not self.connected:
                self.client.connect(host='localhost', port=6600)
                self.connected = True
            self.mpd_status = self.client.status()
            self.current_song = self.client.currentsong()
        except:
            self.connected = False

    def render(self):
        if not self.mpd_status:
            return

        if 'state' in self.mpd_status and self.mpd_status['state'] == 'play':
            set_icon(self._status_icon_label, 'play')
        else:
            set_icon(self._status_icon_label, 'pause')

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
                set_icon(self._shuffle_icon_label, 'shuffle-on')
            else:
                set_icon(self._shuffle_icon_label, 'shuffle-off')

    def format_seconds(self, seconds):
        seconds = math.floor(float(seconds))
        return '%02d:%02d' % (seconds // 60, seconds % 60)
