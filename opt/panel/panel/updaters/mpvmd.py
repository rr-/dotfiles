import json
import os
import socket
import time
import typing as T

from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater
from panel.util import exception_guard

SOCKET_PATH = "/tmp/mpvmd.socket"


class MpvmdConnection(QtCore.QThread):
    property_changed = QtCore.pyqtSignal(str, object)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        self._request_id = 0
        self._messages: T.Dict[int, T.Any] = {}
        self._socket: T.Optional[socket.socket] = None
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            if not self.is_connected:
                try:
                    self._connect()
                except ConnectionRefusedError:
                    time.sleep(1)
                    continue

            for event in self._recv():
                self._process_event(event)

    @property
    def is_connected(self) -> bool:
        return self._socket is not None

    def _process_event(self, event: T.Any) -> None:
        with exception_guard():
            if event.get("event") == "property-change":
                self.property_changed.emit(event["name"], event["data"])
            elif event.get("request_id"):
                message = self._messages[event["request_id"]]
                if message["command"][0] == "get_property":
                    self.property_changed.emit(
                        message["command"][1], event["data"]
                    )
                del self._messages[event["request_id"]]

    def _connect(self) -> None:
        if self.is_connected:
            return

        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.settimeout(3)
        self._socket.setblocking(True)

        try:
            self._socket.connect(SOCKET_PATH)
        except ConnectionRefusedError:
            self._socket = None
            raise

        self._request_id = 1

        properties = [
            "pause",
            "time-pos",
            "duration",
            "script-opts",
            "metadata",
            "path",
        ]
        for i, name in enumerate(properties, 1):
            self.send(["observe_property", i, name])
            self.send(["get_property", name])

    def send(self, command: T.List[T.Any]) -> None:
        if not self.is_connected:
            raise ValueError("not connected")

        message = {"command": command, "request_id": self._request_id}
        self._send(message)
        self._messages[self._request_id] = message
        self._request_id += 1

    def _send(self, message: T.Any) -> None:
        assert self._socket is not None
        try:
            self._socket.send((json.dumps(message) + "\n").encode())
        except (BrokenPipeError, ValueError):
            self._socket = None
            raise

    def _recv(self) -> T.List[T.Any]:
        assert self._socket is not None
        data = b""
        try:
            while True:
                chunk = self._socket.recv(1024)
                data += chunk
                if chunk.endswith(b"\n") or not chunk:
                    break
        except (BrokenPipeError, ValueError):
            self._socket = None
            raise
        ret = []
        for line in data.decode().split("\n"):
            if line:
                ret.append(json.loads(line))
        return ret


class MpvmdUpdater(BaseUpdater):
    is_paused_changed = QtCore.pyqtSignal(bool)
    is_shuffle_enabled_changed = QtCore.pyqtSignal(bool)
    elapsed_changed = QtCore.pyqtSignal(int)
    duration_changed = QtCore.pyqtSignal(int)
    path_changed = QtCore.pyqtSignal(str)
    metadata_changed = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._is_paused = False
        self._is_shuffle_enabled = False
        self._elapsed = 0
        self._duration = 0
        self._path = ""
        self._metadata: T.Dict[str, T.Any] = {}
        self._script_opts: T.Dict[str, T.Any] = {}

        self._connection = MpvmdConnection(self)
        if self.is_available:
            self._connection.start()

        self._connection.property_changed.connect(self._on_property_change)

    @property
    def is_available(self) -> bool:
        return os.path.exists(SOCKET_PATH)

    @property
    def elapsed(self) -> int:
        return self._elapsed

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @is_paused.setter
    def is_paused(self, is_paused: bool) -> None:
        self._connection.send(
            ["set_property", "pause", "yes" if is_paused else "no"]
        )

    @property
    def is_shuffle_enabled(self) -> bool:
        return self._script_opts.get("random_playback", "no") == "yes"

    @is_shuffle_enabled.setter
    def is_shuffle_enabled(self, is_shuffle_enabled: bool) -> None:
        data = self._script_opts.copy()
        data["random_playback"] = "yes" if is_shuffle_enabled else "no"
        self._connection.send(["set_property", "script-opts", data])

    @property
    def path(self) -> str:
        return self._path

    @property
    def metadata(self) -> T.Dict[str, T.Any]:
        return self._metadata

    def prev_track(self) -> None:
        self._connection.send(
            ["script-message-to", "playlist", "playlist-prev"]
        )

    def next_track(self) -> None:
        self._connection.send(
            ["script-message-to", "playlist", "playlist-next"]
        )

    def _on_property_change(self, key: str, value: T.Any) -> None:
        if key == "pause" and value != self._is_paused:
            self._is_paused = value
            self.is_paused_changed.emit(self._is_paused)

        if key == "script-opts":
            old_value = self.is_shuffle_enabled
            self._script_opts = value
            new_value = self.is_shuffle_enabled
            if old_value != new_value:
                self.is_shuffle_enabled_changed.emit(new_value)

        if key == "time-pos" and value != self._elapsed:
            self._elapsed = value
            self.elapsed_changed.emit(value)

        if key == "duration" and value != self._duration:
            self._duration = value
            self.duration_changed.emit(value)

        if key == "path" and value != self._path:
            self._path = value
            self.path_changed.emit(value)

        if key == "metadata" and value != self._metadata:
            self._metadata = value or {}
            self.metadata_changed.emit(value)
