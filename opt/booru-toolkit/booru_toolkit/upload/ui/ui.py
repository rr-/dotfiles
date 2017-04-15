import asyncio
from typing import Any, Tuple, Set, List
import urwid
from booru_toolkit import util
from booru_toolkit.plugin import PluginBase
from booru_toolkit.upload.ui.common import Tag
from booru_toolkit.upload.ui.common import TagSource
from booru_toolkit.upload.ui.common import TagList
from booru_toolkit.upload.ui.common import unbox_from_ui
from booru_toolkit.upload.ui.fuzzy_input_widget import FuzzyInput
from booru_toolkit.upload.ui.chosen_tags_widget import ChosenTagsListBox


_PALETTE = [
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
]


class Ui:
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

        chosen_tags.on_update.append(self._on_tags_change)

        frame = urwid.Frame(
            None, header=urwid.Text(title, 'center') if title else None)

        self._loop = urwid.MainLoop(
            frame,
            unhandled_input=self._keypress,
            event_loop=urwid.AsyncioEventLoop())
        self._loop.screen.set_terminal_properties(256)
        self._loop.screen.register_palette(_PALETTE)

        self._input_box = urwid.LineBox(
            FuzzyInput(plugin, self._loop), title='Tag input')
        urwid.connect_signal(
            self._input_box.original_widget, 'accept', self._on_tag_accept)

        self._chosen_tags_box = urwid.LineBox(
            ChosenTagsListBox(chosen_tags, plugin),
            title='Chosen tags ({})'.format(len(chosen_tags.get_all())))

        self._columns = urwid.Columns([self._input_box, self._chosen_tags_box])
        self._columns.set_focus(0)
        frame.set_body(self._columns)

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
        self._chosen_tags_box.original_widget.schedule_update()

    def _on_tags_change(self) -> None:
        self._chosen_tags_box.set_title(
            'Chosen tags ({})'.format(len(self._chosen_tags.get_all())))

    def _on_tag_accept(self, _widget: urwid.Widget, text: str) -> None:
        text = unbox_from_ui(text)

        previous_tags = self._chosen_tags.get_all()
        self._chosen_tags.add(text, TagSource.UserInput)

        async def work() -> None:
            await self._chosen_tags_box.original_widget.update()

            async for implication in (
                    self._plugin.get_tag_implications(text)):
                self._chosen_tags.add(implication, TagSource.Implication)
                await self._chosen_tags_box.original_widget.update()

            added_tags = set([
                tag
                for tag in self._chosen_tags.get_all()
                if tag not in previous_tags])
            self._undo_stack.append(added_tags)

        asyncio.ensure_future(work())


async def run(plugin: PluginBase, tag_list: TagList, title: str) -> None:
    with util.redirect_stdio():
        tagger = Ui(tag_list, plugin, title)
        await tagger.add_from_user_input()
