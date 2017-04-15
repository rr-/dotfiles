import asyncio
from typing import Any, Optional, Tuple, List, Dict, Callable
import urwid
from urwid_readline import ReadlineEdit
from booru_toolkit import util
from booru_toolkit.plugin import PluginBase
from booru_toolkit.upload.ui.common import box_to_ui
from booru_toolkit.upload.ui.common import unbox_from_ui


class FuzzyInput(urwid.ListBox):
    signals = ['accept']

    def __init__(self, plugin: PluginBase, main_loop: urwid.MainLoop) -> None:
        self._plugin = plugin
        self._main_loop = main_loop

        self._focus = -1
        self._matches: List[Tuple[str, int]] = []

        self._update_id = 0
        self._update_alarm = None
        self._input_box = ReadlineEdit('', wrap=urwid.CLIP)
        urwid.signals.connect_signal(
            self._input_box, 'change', self._on_text_change)

        super().__init__(urwid.SimpleListWalker([]))
        self._update_widgets()

    def selectable(self) -> bool:
        return True

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        keymap: Dict[str, Callable[[Tuple[int, int]], None]] = {
            'enter':     self._accept,
            'tab':       self._select_prev,
            'shift tab': self._select_next,
        }
        if key in keymap:
            keymap[key](size)
            return None
        return self._input_box.keypress((size[0],), key)

    def _accept(self, _size: Tuple[int, int]) -> None:
        text = self._input_box.text.strip()
        if not text:
            return
        self._input_box.set_edit_text('')
        self._matches = []
        self._focus = -1
        self._update_widgets()
        urwid.signals.emit_signal(self, 'accept', self, text)
        self._invalidate()

    def _select_next(self, _size: Tuple[int, int]) -> None:
        if self._focus > 0:
            self._focus -= 1
            self._on_results_focus_change()
            self._update_widgets()

    def _select_prev(self, size: Tuple[int, int]) -> None:
        if self._focus + 1 < min(len(self._matches), size[1] - 1):
            self._focus += 1
            self._on_results_focus_change()
            self._update_widgets()

    def _on_text_change(self, *_args: Any, **_kwargs: Any) -> None:
        if self._update_alarm:
            self._main_loop.remove_alarm(self._update_alarm)
        self._update_alarm = self._main_loop.set_alarm_in(
            0.05, lambda *_: self._schedule_update_matches())

    def _on_results_focus_change(self, *_args: Any, **_kwargs: Any) -> None:
        urwid.signals.disconnect_signal(
            self._input_box, 'change', self._on_text_change)
        self._input_box.set_edit_text(
            box_to_ui(self._matches[self._focus][0]))
        self._input_box.set_edit_pos(len(self._input_box.text))
        urwid.signals.connect_signal(
            self._input_box, 'change', self._on_text_change)

    def _schedule_update_matches(self) -> None:
        asyncio.ensure_future(self._update_matches())

    async def _update_matches(self) -> None:
        text = unbox_from_ui(self._input_box.text)
        self._update_id += 1
        update_id = self._update_id

        tag_names = await self._plugin.find_tags(text)
        if self._update_id > update_id:
            return

        matches = []
        for tag_name in tag_names:
            tag_usage_count = (
                await self._plugin.get_tag_usage_count(tag_name))
            matches.append((tag_name, tag_usage_count))

        self._matches = matches
        self._focus = util.clamp(self._focus, -1, len(self._matches) - 1)
        self._update_widgets()

    def _update_widgets(self) -> None:
        new_list: List[urwid.Widget] = [self._input_box]
        for i, (tag_name, tag_usage_count) in enumerate(self._matches):
            attr_name = 'match'
            if i == self._focus:
                attr_name = 'f-' + attr_name
            columns_widget = urwid.Columns([
                (urwid.Text(box_to_ui(tag_name), wrap=urwid.CLIP)),
                (urwid.PACK, urwid.Text(str(tag_usage_count))),
            ])
            new_list.append(urwid.AttrWrap(columns_widget, attr_name))
        list.clear(self.body)
        self.body.extend(new_list)
        self.body.set_focus(0)
