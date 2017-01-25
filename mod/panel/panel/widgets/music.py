import math
from PyQt5 import QtWidgets
from mpd import MPDClient
from panel.widgets.widget import Widget


class MpdWidget(Widget):
    delay = 1

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self.client = MPDClient()
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
        with self.exception_guard():
            self.client.pause()
            self.refresh()
            self.render()

    def prev_or_next_track(self, event):
        with self.exception_guard():
            if event.angleDelta().y() > 0:
                self.client.next()
            else:
                self.client.previous()
            self.refresh()
            self.render()

    def shuffle_clicked(self, _event):
        with self.exception_guard():
            self.client.random(int(self.client.status()['random'] == '0'))
            self.refresh()
            self.render()

    def refresh_impl(self):
        if not self.client._sock:
            self.client.connect(host='localhost', port=6600)
        try:
            self.mpd_status = self.client.status()
            self.current_song = self.client.currentsong()
        except BrokenPipeError:
            self.client.disconnect()
            raise

    def render_impl(self):
        if not self.mpd_status:
            return

        if 'state' in self.mpd_status and self.mpd_status['state'] == 'play':
            self.set_icon(self._status_icon_label, 'play')
        else:
            self.set_icon(self._status_icon_label, 'pause')

        text = ''
        if self.current_song:
            if 'title' not in self.current_song \
                    or not str(self.current_song['title']).strip():
                text = self.current_song['file']
            else:
                if 'artist' in self.current_song:
                    text = str(self.current_song['artist']) + ' - '
                text += str(self.current_song['title'])
            if 'elapsed' in self.mpd_status and 'time' in self.current_song:
                text += ' %s / %s' % (
                    self.format_seconds(self.mpd_status['elapsed']),
                    self.format_seconds(self.current_song['time']))
        self._song_label.setText(text)

        shuffle = 'random' in self.mpd_status \
            and self.mpd_status['random'] == '1'
        if self._shuffle_icon_label.property('active') != shuffle:
            self._shuffle_icon_label.setProperty('active', shuffle)
            if shuffle:
                self.set_icon(self._shuffle_icon_label, 'shuffle-on')
            else:
                self.set_icon(self._shuffle_icon_label, 'shuffle-off')

    def format_seconds(self, seconds):
        seconds = math.floor(float(seconds))
        return '%02d:%02d' % (seconds // 60, seconds % 60)
