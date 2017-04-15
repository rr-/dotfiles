#!/bin/python3
# Interactive stand-alone tagger for ul-gelbooru, ul-yume etc.

import os
import sys
import asyncio
import textwrap
import concurrent.futures
from enum import Enum
from typing import Any, Optional, Tuple, Set, List, Dict, Callable
import urwid
from urwid_readline import ReadlineEdit
from booru_toolkit.plugin import PluginBase


WidgetSize = Tuple[int, int]


def _box_to_ui(text: str) -> str:
    return text.replace('_', ' ')


def _unbox_from_ui(text: str) -> str:
    return text.replace(' ', '_')


def _clamp(number: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, number))


class TagSource(Enum):
    Initial = 0
    UserInput = 1
    Implication = 2


class Tag:
    def __init__(self, name: str, source: TagSource) -> None:
        self.name = name
        self.source = source


class TagList:
    def __init__(self) -> None:
        self._tags: List[Tag] = []

    def get_all(self) -> List[Tag]:
        return sorted(self._tags, key=lambda tag: tag.name)

    def delete(self, tag_to_remove: Tag) -> None:
        self._tags = [
            tag
            for tag in self._tags
            if tag.name.lower() != tag_to_remove.name.lower()
        ]

    def add(self, name: str, source: TagSource) -> None:
        if any(name.lower() == tag.name.lower() for tag in self._tags):
            return
        self._tags.append(Tag(name, source))


class VimListBox(urwid.ListBox):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.num = None

    def selectable(self) -> bool:
        return True

    def keypress(self, _size: WidgetSize, key: str) -> Optional[str]:
        keymap = {
            'j': self._select_prev,
            'k': self._select_next,
            'g': self._select_first,
            'G': self._select_last,
        }
        if key in '0123456789':
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
        return self.body.focus

    @_focus.setter
    def _focus(self, focus: int) -> None:
        self.body.focus = _clamp(focus, 0, len(self.body) - 1)


class ChosenTagsListBox(VimListBox):
    def __init__(
            self,
            chosen_tags: TagList,
            plugin: PluginBase) -> None:
        super().__init__(urwid.SimpleListWalker([]))
        self._chosen_tags = chosen_tags
        self._plugin = plugin
        self.schedule_update()

    def keypress(self, size: WidgetSize, key: str) -> Optional[str]:
        keymap = {
            'd':      self._delete_selected,
            'delete': self._delete_selected,
        }
        if key in keymap:
            keymap[key]()
            self._cancel_num()
            return None
        return super().keypress(size, key)

    def schedule_update(self) -> None:
        asyncio.ensure_future(self.update())

    async def update(self) -> None:
        new_list = []
        for tag in self._chosen_tags.get_all():
            if tag.source == TagSource.Implication:
                attr_name = 'implied-tag'
            elif tag.source == TagSource.Initial:
                attr_name = 'initial-tag'
            elif not await self._plugin.tag_exists(tag.name):
                attr_name = 'new-tag'
            else:
                attr_name = 'tag'
            tag_usage_count = await self._plugin.get_tag_usage_count(tag.name)

            columns_widget = urwid.Columns([
                (urwid.Text(_box_to_ui(tag.name), wrap=urwid.CLIP)),
                (urwid.PACK, urwid.Text(str(tag_usage_count))),
            ])
            setattr(columns_widget, 'tag', tag)
            new_list.append(
                urwid.AttrWrap(columns_widget, attr_name, 'f-' + attr_name))
        self.body.clear()
        self.body.extend(new_list)
        self._invalidate()

    def _delete_selected(self) -> None:
        old_focused_item = self._focus
        self._chosen_tags.delete(self.body.get_focus()[0].tag)
        self.schedule_update()
        self._focus = old_focused_item
        self._invalidate()


class FuzzyInput(urwid.Widget):
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

        self._update_matches()

    def selectable(self) -> bool:
        return True

    def keypress(self, size: WidgetSize, key: str) -> Optional[str]:
        keymap: Dict[str, Callable[[WidgetSize], None]] = {
            'enter':     self._accept,
            'tab':       self._select_prev,
            'shift tab': self._select_next,
        }
        if key in keymap:
            keymap[key](size)
            return None
        return self._input_box.keypress(size, key)

    def render(self, size: WidgetSize, focus: bool = False) -> None:
        maxcol, maxrow = size
        canvases = [(self._input_box.render((maxcol,)), 0, focus)]
        for i in range(min(len(self._matches), maxrow - 1)):
            tag_name, tag_usage_count = self._matches[i]

            column_a = _box_to_ui(tag_name)
            column_b = str(tag_usage_count)

            column_a_len = maxcol - 1 - len(column_b)
            assert column_a_len > 0
            text = textwrap.shorten(column_a, width=column_a_len)
            text += ' ' * (column_a_len - len(text))
            text += ' '
            text += column_b

            attr_name = 'match'
            if self._focus == i:
                attr_name = 'f-' + attr_name
            canvases.append((
                urwid.TextCanvas(
                    [text.encode()],
                    attr=[[(attr_name, len(text))]],
                    maxcol=maxcol),
                i + 1,
                focus))

        canvas = urwid.CanvasCombine(canvases)
        canvas.pad_trim_top_bottom(0, maxrow - len(canvases))
        if focus:
            canvas.cursor = (min(self._input_box.edit_pos, maxcol), 0)
        return canvas

    def _accept(self, _size: WidgetSize) -> None:
        text = self._input_box.text.strip()
        if not text:
            return
        self._input_box.text = ''
        self._update_matches()
        self._focus = -1
        urwid.signals.emit_signal(self, 'accept', self, text)
        self._invalidate()

    def _select_next(self, _size: WidgetSize) -> None:
        if self._focus > 0:
            self._focus -= 1
            self._on_results_focus_change()
            self._invalidate()

    def _select_prev(self, size: WidgetSize) -> None:
        if self._focus + 1 < min(len(self._matches), size[1] - 1):
            self._focus += 1
            self._on_results_focus_change()
            self._invalidate()

    def _on_text_change(self, *_args: Any, **_kwargs: Any) -> None:
        if self._update_alarm:
            self._main_loop.remove_alarm(self._update_alarm)
        self._update_alarm = self._main_loop.set_alarm_in(
            0.05, lambda *_: self._update_matches())

    def _on_results_focus_change(self, *_args: Any, **_kwargs: Any) -> None:
        urwid.signals.disconnect_signal(
            self._input_box, 'change', self._on_text_change)
        self._input_box.text = _box_to_ui(self._matches[self._focus][0])
        self._input_box.edit_pos = len(self._input_box.text)
        urwid.signals.connect_signal(
            self._input_box, 'change', self._on_text_change)

    def _update_matches(self) -> None:
        text = _unbox_from_ui(self._input_box.text)

        self._update_id += 1
        update_id = self._update_id

        async def work() -> None:
            tag_names = await self._plugin.find_tags(text)
            if self._update_id > update_id:
                return

            matches = []
            for tag_name in tag_names:
                tag_usage_count = (
                    await self._plugin.get_tag_usage_count(tag_name))
                matches.append((tag_name, tag_usage_count))

            self._matches = matches
            self._focus = _clamp(self._focus, -1, len(self._matches) - 1)
            self._invalidate()

        asyncio.ensure_future(work())


class UrwidTagger:
    def __init__(
            self,
            chosen_tags: TagList,
            plugin: PluginBase,
            title: str) -> None:
        del urwid.command_map['left']
        del urwid.command_map['down']
        del urwid.command_map['up']
        del urwid.command_map['right']
        self._chosen_tags = chosen_tags
        self._plugin = plugin
        self._undo_stack: List[Set[Tag]] = []
        self._running = True

        frame = urwid.Frame(
            None, header=urwid.Text(title, 'center') if title else None)
        self._loop = urwid.MainLoop(
            frame,
            unhandled_input=self._keypress,
            event_loop=urwid.AsyncioEventLoop())

        self._loop.screen.set_terminal_properties(256)
        self._fuzzy_input = FuzzyInput(plugin, self._loop)
        urwid.connect_signal(
            self._fuzzy_input, 'accept', self._on_tag_accept)

        self._choices_box = ChosenTagsListBox(chosen_tags, plugin)
        self._columns = urwid.Columns([
            urwid.LineBox(self._fuzzy_input, title='Input'),
            urwid.LineBox(self._choices_box, title='Chosen tags')])
        self._columns.set_focus(0)
        frame.set_body(self._columns)

        self._loop.screen.register_palette([
            ('match',         'default',     'default'),
            ('f-match',       'light green', 'default'),
            ('tag',           'default',     'default',  None, None,   None),
            ('new-tag',       'light red',   'default',  None, None,   '#FF0'),
            ('implied-tag',   'light green', 'default',  None, None,   '#DFD'),
            ('initial-tag',   'dark blue',   'default',  None, None,   '#DDF'),
            ('f-tag',         'black',       'white',    None, '#FFF', '#000'),
            ('f-new-tag',     'black',       'white',    None, '#FFF', '#000'),
            ('f-implied-tag', 'black',       'white',    None, '#FFF', '#000'),
            ('f-initial-tag', 'black',       'white',    None, '#FFF', '#000'),
        ])

    async def add_from_user_input(self) -> None:
        self._loop.start()  # we'll manage the loop manually
        try:
            while self._running:
                await asyncio.sleep(0.1)
        finally:
            self._loop.stop()

    def _keypress(self, key: str) -> None:
        keymap = {
            'ctrl q': self._confirm,
            'ctrl x': self._toggle_focus,
            'ctrl r': self._undo_tag,
        }
        if key in keymap:
            keymap[key]()

    def _confirm(self) -> None:
        self._running = False

    def _toggle_focus(self) -> None:
        if self._columns.get_focus_column() == 0:
            self._columns.set_focus(1)
        else:
            self._columns.set_focus(0)

    def _undo_tag(self) -> None:
        if not self._undo_stack:
            return
        for tag in self._undo_stack.pop():
            self._chosen_tags.delete(tag)
        self._choices_box.schedule_update()

    def _on_tag_accept(self, _widget: urwid.Widget, text: str) -> None:
        text = _unbox_from_ui(text)

        previous_tags = self._chosen_tags.get_all()
        self._chosen_tags.add(text, TagSource.UserInput)

        async def work() -> None:
            await self._choices_box.update()

            async for implication in (
                    self._plugin.get_tag_implications(text)):
                self._chosen_tags.add(implication, TagSource.Implication)
                await self._choices_box.update()

            added_tags = set([
                tag
                for tag in self._chosen_tags.get_all()
                if tag not in previous_tags])
            self._undo_stack.append(added_tags)

        asyncio.ensure_future(work())


def _open_tty() -> Tuple[Any, Any]:
    saved_stdin = os.dup(sys.stdin.fileno())
    saved_stdout = os.dup(sys.stdout.fileno())
    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    sys.stdin = open('/dev/tty', 'r')
    sys.stdout = open('/dev/tty', 'w')
    return saved_stdin, saved_stdout


def _restore_stdio(saved_stdin: Any, saved_stdout: Any) -> None:
    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    os.dup(saved_stdin)
    os.dup(saved_stdout)


async def run(plugin: PluginBase, tag_list: TagList, title: str) -> None:
    saved_fds = _open_tty()
    tagger = UrwidTagger(tag_list, plugin, title)
    try:
        await tagger.add_from_user_input()
    finally:
        _restore_stdio(*saved_fds)
