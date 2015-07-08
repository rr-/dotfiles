from PyQt4 import QtGui
from PyQt4 import QtCore

class FlowLayout(QtGui.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1, rtl=False):
        super().__init__(parent)
        self.rtl = rtl
        if parent is not None:
            self.setMargin(margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):
        y = rect.y()
        if self.rtl:
            x = rect.x() + rect.width()
            for item in reversed(self.itemList):
                x -= item.sizeHint().width()
                if not testOnly:
                    item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
                x -= self.spacing()
        else:
            x = rect.x()
            for item in self.itemList:
                if not testOnly:
                    item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
                x += item.sizeHint().width() + self.spacing()
        if not self.itemList:
            return 0
        return max([item.sizeHint().height() for item in self.itemList])

