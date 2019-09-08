import argparse
import enum
import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand, CommandUnavailable
from bubblesub.cfg.menu import MenuCommand
from bubblesub.cmd.common import SubtitlesSelection
from bubblesub.fmt.ass.event import AssEvent
from bubblesub.ui.util import Dialog, async_dialog_exec
from bubblesub.util import ms_to_str

try:
    import cv2
    import numpy as np
    import pytesseract
except ImportError as ex:
    raise CommandUnavailable("numpy is not installed")


class OcrSettings(QtCore.QObject):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.threshold = 128
        self.invert = False
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.dilate = False
        self.erode = False


class DragMode(enum.IntEnum):
    none = enum.auto()
    end = enum.auto()


class _PreviewWidget(QtWidgets.QWidget):
    def __init__(
        self, parent: QtWidgets.QWidget, frame: np.array, settings: OcrSettings
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.frame = frame
        self.bitmap = np.zeros(frame.shape)
        self.drag = DragMode.none

        self.settings.changed.connect(self.on_settings_change)

        self.on_settings_change()

    def on_settings_change(self) -> None:
        self.update_bitmap()
        self.update()

    def sizeHint(self) -> QtCore.QSize:
        height, width, _channels = self.frame.shape
        return QtCore.QSize(width, height)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.settings.x2 = event.pos().x()
            self.settings.y2 = event.pos().y()

        if self.settings.x1 > self.settings.x2:
            self.settings.x2, self.settings.x1 = (
                self.settings.x1,
                self.settings.x2,
            )
        if self.settings.y1 > self.settings.y2:
            self.settings.y2, self.settings.y1 = (
                self.settings.y1,
                self.settings.y2,
            )

        self.settings.changed.emit()

        self.drag = DragMode.none
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.drag = DragMode.end
            self.settings.x1 = self.settings.x2 = event.pos().x()
            self.settings.y1 = self.settings.y2 = event.pos().y()
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.drag == DragMode.end:
            self.settings.x2 = event.pos().x()
            self.settings.y2 = event.pos().y()
        self.update()

    def update_bitmap(self) -> None:
        self.bitmap = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        _, self.bitmap = cv2.threshold(
            self.bitmap, self.settings.threshold, 255, cv2.THRESH_BINARY
        )
        if self.settings.invert:
            self.bitmap = 255 - self.bitmap
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        if self.settings.dilate:
            self.bitmap = cv2.dilate(self.bitmap, kernel, 1)
        if self.settings.erode:
            self.bitmap = cv2.erode(self.bitmap, kernel, 1)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()

        painter.begin(self)
        image = QtGui.QImage(
            self.bitmap.data,
            self.bitmap.shape[1],
            self.bitmap.shape[0],
            self.bitmap.strides[0],
            QtGui.QImage.Format_Grayscale8,
        )
        painter.drawPixmap(0, 0, QtGui.QPixmap.fromImage(image))

        if (
            self.settings.x1
            and self.settings.y1
            and self.settings.x2
            and self.settings.y2
        ):
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(
                QtCore.QRect(
                    self.settings.x1,
                    self.settings.y1,
                    self.settings.x2 - self.settings.x1,
                    self.settings.y2 - self.settings.y1,
                )
            )

            painter.setPen(QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine))
            painter.drawRect(
                self.settings.x1 + 1,
                self.settings.y1 + 1,
                self.settings.x2 - self.settings.x1,
                self.settings.y2 - self.settings.y1,
            )

        painter.end()


class _Dialog(Dialog):
    def __init__(
        self,
        api: Api,
        main_window: QtWidgets.QMainWindow,
        lang: str,
        events: T.List[AssEvent],
    ) -> None:
        super().__init__(main_window)
        self.setWindowTitle("OCR")

        self.lang = lang
        self.events = events

        self.frame = api.video.get_frame(
            api.video.frame_idx_from_pts(api.playback.current_pts),
            width=api.video.width,
            height=api.video.height,
        ).copy()

        self.settings = OcrSettings(self)
        self.preview_image = _PreviewWidget(self, self.frame, self.settings)
        self.preview_label = QtWidgets.QLabel(self)

        self.invert_checkbox = QtWidgets.QCheckBox(
            self, text="Invert bitmap", checked=self.settings.invert
        )
        self.dilate_checkbox = QtWidgets.QCheckBox(
            self, text="Dilate", checked=self.settings.dilate
        )
        self.erode_checkbox = QtWidgets.QCheckBox(
            self, text="Dilate", checked=self.settings.erode
        )
        self.threshold_slider = QtWidgets.QSlider(
            self,
            minimum=0,
            maximum=255,
            value=self.settings.threshold,
            orientation=QtCore.Qt.Horizontal,
        )

        strip = QtWidgets.QDialogButtonBox(self)
        self.commit_btn = strip.addButton("Commit", strip.ActionRole)
        strip.addButton("Close", strip.RejectRole)

        self.threshold_slider.valueChanged.connect(self.on_threshold_change)
        self.invert_checkbox.clicked.connect(self.on_invert_change)
        self.dilate_checkbox.clicked.connect(self.on_dilate_change)
        self.erode_checkbox.clicked.connect(self.on_erode_change)
        self.settings.changed.connect(self.on_settings_change)
        strip.clicked.connect(self.action)
        strip.accepted.connect(self.accept)
        strip.rejected.connect(self.reject)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.invert_checkbox)
        top_layout.addWidget(self.dilate_checkbox)
        top_layout.addWidget(self.erode_checkbox)
        top_layout.addWidget(QtWidgets.QLabel("Threshold:", self))
        top_layout.addWidget(self.threshold_slider)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(24)
        layout.addLayout(top_layout)
        layout.addWidget(self.preview_image)
        layout.addWidget(self.preview_label)
        layout.addWidget(strip)

        self.on_settings_change()

    def on_invert_change(self) -> None:
        self.settings.invert = self.invert_checkbox.isChecked()
        self.settings.changed.emit()

    def on_dilate_change(self) -> None:
        self.settings.dilate = self.dilate_checkbox.isChecked()
        self.settings.changed.emit()

    def on_erode_change(self) -> None:
        self.settings.erode = self.erode_checkbox.isChecked()
        self.settings.changed.emit()

    def on_threshold_change(self) -> None:
        self.settings.threshold = self.threshold_slider.value()
        self.settings.changed.emit()

    def on_settings_change(self) -> None:
        self.update_preview()

    def update_preview(self) -> None:
        img = self.preview_image.bitmap[
            self.settings.y1 : self.settings.y2,
            self.settings.x1 : self.settings.x2,
        ]
        #cv2.imwrite("/home/rr-/test.png", img)

        try:
            text = pytesseract.image_to_string(img, self.lang)
        except SystemError:
            text = ""

        if self.lang in {"jpn"}:
            text = text.replace(" ", "")

        self.preview_label.setText(text)

    def action(self, sender: QtWidgets.QAbstractButton) -> None:
        if sender == self.commit_btn:
            self.commit()

    def commit(self) -> None:
        for event in self.events:
            event.note += self.preview_label.text()


class OCRCommand(BaseCommand):
    names = ["ocr"]
    help_text = "Perform optical recognition on given frame."

    @property
    def is_enabled(self):
        return self.api.video.is_ready and self.args.target.makes_sense

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-t",
            "--target",
            help="subtitles to process",
            type=lambda value: SubtitlesSelection(api, value),
            default="selected",
        )
        parser.add_argument(
            "-l",
            "--lang",
            "--language",
            help="language used for detection",
            default="jpn",
        )

    async def run(self):
        await self.api.gui.exec(self._run_with_gui)

    async def _run_with_gui(self, main_window: QtWidgets.QMainWindow) -> None:
        events = list(await self.args.target.get_subtitles())
        dialog = _Dialog(self.api, main_window, self.args.lang, events)
        with self.api.undo.capture():
            await async_dialog_exec(dialog)


COMMANDS = [OCRCommand]
MENU = [MenuCommand("&OCR", "ocr")]
