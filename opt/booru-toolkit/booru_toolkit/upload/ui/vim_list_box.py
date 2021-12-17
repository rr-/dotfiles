from typing import Any, cast

import urwid

from booru_toolkit import util


class VimListBox(urwid.ListBox):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.num: int | None = None

    def selectable(self) -> bool:
        return True

    def keypress(self, _size: tuple[int, int], key: str) -> str | None:
        keymap = {
            "j": self._select_prev,
            "k": self._select_next,
            "g": self._select_first,
            "G": self._select_last,
        }
        if key in "0123456789":
            self.num = (0 if self.num is None else self.num) * 10 + int(key)
            return None
        elif key in keymap:
            keymap[key]()
            self._cancel_num()
            return None
        return key

    def _cancel_num(self) -> None:
        self.num = None

    def _select_next(self) -> None:
        num = self.num if self.num is not None else 1
        self._focus -= num
        self._invalidate()

    def _select_prev(self) -> None:
        num = self.num if self.num is not None else 1
        self._focus += num
        self._invalidate()

    def _select_first(self) -> None:
        if self.num is not None:
            self._focus = self.num - 1
        else:
            self._focus = 0
        self._invalidate()

    def _select_last(self) -> None:
        if self.num is not None:
            self._focus = self.num - 1
        else:
            self._focus = len(self.body) - 1
        self._invalidate()

    @property
    def _focus(self) -> int:
        return cast(int, self.body.focus)

    @_focus.setter
    def _focus(self, focus: int) -> None:
        self.body.focus = util.clamp(focus, 0, len(self.body) - 1)
