from PyQt5 import QtCore

from panel.updaters.base import BaseUpdater

try:
    import alsaaudio
except ImportError:
    alsaaudio = None


DEVICE = "pulse"


def clip(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


class VolumeUpdater(BaseUpdater):
    mute_changed = QtCore.pyqtSignal()
    volume_changed = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        if alsaaudio:
            try:
                self.mixer = alsaaudio.Mixer(device=DEVICE)
            except alsaaudio.ALSAAudioError:
                self.mixer = None
        else:
            self.mixer = None

    @property
    def is_available(self) -> bool:
        return self.mixer is not None

    @property
    def is_muted(self) -> bool:
        return self.mixer.getmute()[0]

    @is_muted.setter
    def is_muted(self, value: bool) -> None:
        self.mixer.setmute(value)
        self.mute_changed.emit()

    @property
    def volume(self) -> int:
        return self.mixer.getvolume()[0]

    @volume.setter
    def volume(self, volume: int) -> None:
        self.mixer.setvolume(clip(volume, 0, 100))
        self.volume_changed.emit()
