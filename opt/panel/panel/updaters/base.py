from PyQt5 import QtCore


class BaseUpdater(QtCore.QObject):
    @property
    def is_available(self) -> None:
        raise NotImplementedError('not implemented')
