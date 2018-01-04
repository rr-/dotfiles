import os
import math
import json
import struct
import socket
from typing import Optional, Dict
from PyQt5 import QtWidgets
from panel.widgets.widget import Widget


def _format_time(seconds):
    seconds = math.floor(float(seconds))
    return '%02d:%02d' % (seconds // 60, seconds % 60)


class MpvmdWidget(Widget):
    delay = 0.5

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        self._socket = None
        self._info = None

        self._container = QtWidgets.QWidget()
        self._status_icon_label = QtWidgets.QLabel(self._container)
        self._song_label = QtWidgets.QLabel(self._container)
        self._shuffle_icon_label = QtWidgets.QLabel(self._container)

        layout = QtWidgets.QHBoxLayout(self._container, margin=0, spacing=6)
        layout.addWidget(self._status_icon_label)
        layout.addWidget(self._song_label)
        layout.addWidget(self._shuffle_icon_label)

        self._status_icon_label.mouseReleaseEvent = self._play_pause_clicked
        self._song_label.mouseReleaseEvent = self._play_pause_clicked
        self._shuffle_icon_label.mouseReleaseEvent = self._shuffle_clicked
        self._status_icon_label.wheelEvent = self._prev_or_next_track
        self._song_label.wheelEvent = self._prev_or_next_track

        try:
            self._refresh_impl()
        except Exception:
            return

    @property
    def container(self):
        return self._container

    @property
    def available(self):
        return self._info is not None

    def _play_pause_clicked(self, _event):
        with self.exception_guard():
            if self._info['paused']:
                self._send({'msg': 'play'})
            else:
                self._send({'msg': 'pause'})
            self._recv()
            self.refresh()
            self.render()

    def _prev_or_next_track(self, event):
        with self.exception_guard():
            if event.angleDelta().y() > 0:
                self._send({'msg': 'playlist-next'})
            else:
                self._send({'msg': 'playlist-prev'})
            self._recv()
            self.refresh()
            self.render()

    def _shuffle_clicked(self, _event):
        with self.exception_guard():
            self._send({'msg': 'random', 'random': not self._info['random']})
            self._recv()
            self.refresh()
            self.render()

    def _refresh_impl(self):
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._socket.settimeout(3)
                self._socket.connect(('localhost', 36934))
            except ConnectionRefusedError:
                self.delay = min(60, self.delay + 1)
                raise

        try:
            self._send({'msg': 'info'})
            self._info = self._recv()
            self.delay = 0.5
        except (BrokenPipeError, ValueError):
            self._socket = None
            self.delay = min(60, self.delay + 1)
            raise

    def _render_impl(self):
        if self._info['paused']:
            self._set_icon(self._status_icon_label, 'pause')
        else:
            self._set_icon(self._status_icon_label, 'play')

        metadata = {k.lower(): v for k, v in self._info['metadata'].items()}

        elapsed = self._info['time-pos']
        duration = self._info['duration']

        text = ''
        if metadata.get('title'):
            if metadata.get('artist'):
                text = metadata['artist'] + ' - ' + metadata['title']
            else:
                text = metadata['title']
        elif metadata.get('icy-title'):
            text = metadata['icy-title']
        else:
            text = os.path.basename(self._info['path'] or '')

        if elapsed and duration:
            text += ' %s / %s' % (
                _format_time(elapsed), _format_time(duration))

        self._song_label.setText(text)

        shuffle = self._info['random']
        if self._shuffle_icon_label.property('active') != shuffle:
            self._shuffle_icon_label.setProperty('active', shuffle)
            if shuffle:
                self._set_icon(self._shuffle_icon_label, 'shuffle-on')
            else:
                self._set_icon(self._shuffle_icon_label, 'shuffle-off')

    def _recv(self) -> Optional[Dict]:
        data_size_raw = self._socket.recv(4)
        if not data_size_raw:
            return None
        data_size = struct.unpack('<I', data_size_raw)[0]
        data = self._socket.recv(data_size)
        return json.loads(data.decode('utf-8'))

    def _send(self, message: Dict):
        data = json.dumps(message).encode('utf-8')
        self._socket.send(struct.pack('<I', len(data)))
        self._socket.send(data)
