import os
import sys
from PyQt5 import QtCore, QtGui


def set_icon(widget, icon_name):
    if widget.property('icon_name') == icon_name:
        return
    widget.setProperty('icon_name', icon_name)
    icon = QtGui.QIcon(QtGui.QPixmap(
        os.path.join(sys.path[0], 'icons', icon_name + '.svg')))
    widget.setPixmap(icon.pixmap(QtCore.QSize(18, 18)))
