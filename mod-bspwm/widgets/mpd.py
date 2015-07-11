import math
import mpd
import subprocess
from PyQt4 import QtGui

class MpdProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.enabled = len(main_window) > 1
        if not self.enabled:
            return

        self.main_window = main_window
        self.client = mpd.MPDClient()
        self.connected = False
        self.mpd_status = None

        self.status_label = QtGui.QLabel()
        self.status_label.setProperty('class', 'icon')
        self.status_label.setStyleSheet('QWidget { margin-right: -8px }')
        self.song_label = QtGui.QLabel()
        self.random_label = QtGui.QLabel()
        self.random_label.setProperty('class', 'icon')
        self.random_label.setText('\U0001F500')

        for w in [self.status_label, self.song_label, self.random_label]:
            main_window[len(main_window) - 1].right_widget.layout().addWidget(w)

        self.status_label.mouseReleaseEvent = self.play_pause_clicked
        self.song_label.mouseReleaseEvent = self.play_pause_clicked
        self.random_label.mouseReleaseEvent = self.random_clicked

    def play_pause_clicked(self, event):
        subprocess.call(['mpc', 'toggle'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.refresh()
        self.render()

    def random_clicked(self, event):
        subprocess.call(['mpc', 'random'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.refresh()
        self.render()

    def refresh(self):
        if not self.enabled:
            return
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
        if not self.enabled or not self.mpd_status:
            return

        if 'state' in self.mpd_status and self.mpd_status['state'] == 'play':
            self.status_label.setText('\u23f5')
        else:
            self.status_label.setText('\u23f8')

        text = ''
        if self.current_song:
            if 'title' not in self.current_song or self.current_song['title'].strip() == '':
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
        self.song_label.setText(text)

        random = 'random' in self.mpd_status and self.mpd_status['random'] == '1'
        new_status = '%s' % random
        if self.random_label.property('active') != new_status:
            self.random_label.setProperty('active', '%s' % random)
            self.main_window.reloadStyleSheet()

    def format_seconds(self):
        seconds = math.floor(float(seconds))
        return '%02d:%02d' % (seconds // 60, seconds % 60)
