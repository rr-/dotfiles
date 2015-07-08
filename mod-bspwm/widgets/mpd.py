import math
import mpd
from PyQt4 import QtGui

class MpdProvider(object):
    delay = 1

    def __init__(self, main_window):
        self.client = mpd.MPDClient()
        self.connected = False
        self.label = QtGui.QLabel()
        main_window[0].left_widget.layout().addWidget(self.label)
        self.mpd_status = None

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

        text = ''
        if 'state' in self.mpd_status and self.mpd_status['state'] == 'play':
            text = '(playing) '
        else:
            text = '(stopped) '

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

        text += ' Random: '
        if 'random' not in self.mpd_status or self.mpd_status['random'] != '1':
            text += 'off'
        else:
            text += 'on'
        self.label.setText(text)

    def format_seconds(self):
        seconds = math.floor(float(seconds))
        return '%02d:%02d' % (seconds // 60, seconds % 60)

