"""Raw terminal input and output."""

import os
import re
import select
import signal
import termios
import tty
import unicodedata
from typing import NamedTuple

from .theme import Style, role, sgr

TAB = 4
MOUSE_RE = re.compile(rb"\x1b\[<(\d+);(\d+);(\d+)([Mm])")


class Mouse(NamedTuple):
    """An SGR mouse report: cells count from 1, wheel buttons are 64+."""

    button: int
    x: int
    y: int
    press: bool


def cwidth(ch: str) -> int:
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def expand(chars: list[tuple[str, Style]]) -> list[tuple[str, int, Style]]:
    """Lay text out in cells: tabs become spaces, control bytes become ^X."""
    out: list[tuple[str, int, Style]] = []
    col = 0
    for ch, style in chars:
        if ch == "\t":
            n = TAB - col % TAB
            out.extend([(" ", 1, style)] * n)
            col += n
        elif ord(ch) < 32 or ch == "\x7f":
            faint = style._replace(fg=role("text.faint"))
            out += [("^", 1, faint), (chr(ord(ch) ^ 64), 1, faint)]
            col += 2
        else:
            w = cwidth(ch)
            out.append((ch, w, style))
            col += w
    return out


class LineBuf:
    def __init__(self, width: int) -> None:
        self.width = width
        self.col = 0
        self.parts: list[str] = []
        self.last: Style | None = None

    def put(self, ch: str, w: int, style: Style) -> bool:
        if self.col + w > self.width:
            return False
        if style != self.last:
            self.parts.append(sgr(style))
            self.last = style
        self.parts.append(ch)
        self.col += w
        return True

    def add(self, text: str, style: Style) -> None:
        for ch, w, st in expand([(ch, style) for ch in text]):
            if not self.put(ch, w, st):
                break

    def add_clipped(self, text: str, style: Style, room: int) -> None:
        """Add text, cut with an ellipsis if it is wider than room."""
        if sum(cwidth(ch) for ch in text) > room:
            while text and sum(cwidth(ch) for ch in text) > room - 1:
                text = text[:-1]
            text += "…"
        self.add(text, style)

    def fill(self, style: Style, upto: int | None = None) -> None:
        upto = self.width if upto is None else min(upto, self.width)
        while self.col < upto:
            self.put(" ", 1, style)

    def render(self) -> str:
        return "".join(self.parts) + "\x1b[0m"


KEYS_CSI = {
    "A": "up",
    "B": "down",
    "C": "right",
    "D": "left",
    "H": "home",
    "F": "end",
    "1~": "home",
    "7~": "home",
    "4~": "end",
    "8~": "end",
    "3~": "delete",
    "5~": "pgup",
    "6~": "pgdn",
    "1;5C": "C-right",
    "1;5D": "C-left",
    "1;3C": "C-right",
    "1;3D": "C-left",
}


class Terminal:
    # Clicks and the wheel come as SGR reports. Shift and drag still
    # selects text in most terminals.
    ENTER = "\x1b[?1049h\x1b[?25l\x1b[?7l\x1b[?1000h\x1b[?1006h"
    LEAVE = "\x1b[?1006l\x1b[?1000l\x1b[?7h\x1b[?25h\x1b[?1049l"

    def __enter__(self) -> "Terminal":
        self.fd = os.open("/dev/tty", os.O_RDWR)
        self.saved = termios.tcgetattr(self.fd)
        self.buf = b""
        self.wake_r, self.wake_w = os.pipe()
        os.set_blocking(self.wake_w, False)
        signal.signal(signal.SIGWINCH, lambda *_: self._wake())
        self.resume()
        return self

    def __exit__(self, *_) -> None:
        self.suspend()
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)
        os.close(self.fd)

    def _wake(self) -> None:
        try:
            os.write(self.wake_w, b"x")
        except BlockingIOError:
            pass

    def suspend(self) -> None:
        self.write(self.LEAVE)
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)

    def resume(self) -> None:
        tty.setraw(self.fd)
        self.write(self.ENTER)

    def write(self, text: str) -> None:
        data = text.encode()
        while data:
            data = data[os.write(self.fd, data) :]

    def size(self) -> tuple[int, int]:
        size = os.get_terminal_size(self.fd)
        return size.columns, size.lines

    def _fill(self, timeout: float | None) -> bool:
        ready, _, _ = select.select([self.fd, self.wake_r], [], [], timeout)
        if self.wake_r in ready:
            os.read(self.wake_r, 1024)
        if self.fd in ready:
            self.buf += os.read(self.fd, 4096)
            return True
        return False

    def read_key(self) -> str | Mouse | None:
        """The next key, or None when the terminal was resized."""
        if not self.buf and not self._fill(None):
            return None
        if self.buf[:1] == b"\x1b":
            if len(self.buf) == 1:
                self._fill(0.03)
            if self.buf[:3] == b"\x1b[<" and not MOUSE_RE.match(self.buf):
                self._fill(0.03)
            if m := MOUSE_RE.match(self.buf):
                self.buf = self.buf[m.end() :]
                return Mouse(int(m[1]), int(m[2]), int(m[3]), m[4] == b"M")
            m = re.match(
                rb"\x1b(?:\[([0-9;]*[~A-Za-z])|O([A-Za-z]))", self.buf
            )
            if m:
                self.buf = self.buf[m.end() :]
                code = (m[1] or m[2]).decode()
                return KEYS_CSI.get(code, f"<{code}>")
            # Alt and a key comes as ESC and the key: M-b, never a lone Esc
            # with a stray b after it.
            if len(self.buf) > 1 and self.buf[1] != 0x1B:
                self.buf = self.buf[1:]
                key = self.read_key()
                if isinstance(key, str) and (
                    len(key) == 1
                    or key
                    in (
                        "backspace",
                        "enter",
                        "tab",
                    )
                ):
                    return f"M-{key}"
                return key
            self.buf = self.buf[1:]
            return "esc"
        lead = self.buf[0]
        need = (
            1 if lead < 0xC0 else 2 if lead < 0xE0 else 3 if lead < 0xF0 else 4
        )
        while len(self.buf) < need and self._fill(0.05):
            pass
        chunk, self.buf = self.buf[:need], self.buf[need:]
        ch = chunk.decode(errors="replace")
        if ch == "\r":
            return "enter"
        if ch == "\t":
            return "tab"
        if ch in "\x7f\x08":
            return "backspace"
        if len(ch) == 1 and ord(ch) < 32:
            return f"C-{chr(ord(ch) + 96)}"
        return ch
