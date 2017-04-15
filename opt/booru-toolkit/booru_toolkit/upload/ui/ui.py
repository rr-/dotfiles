import asyncio
from typing import Any, Tuple, Set, List
import urwid
from booru_toolkit import util
from booru_toolkit.plugin import PluginBase
from booru_toolkit.plugin import Safety
from booru_toolkit.upload import common
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


class TableColumn(urwid.Pile):
    def pack(
            self,
            size: Tuple[int, int],
            focus: bool = False) -> Tuple[int, int]:
        maxcol = size[0]
        maximum = max([i[0].pack((maxcol,), focus)[0] for i in self.contents])
        return (min(maximum, maxcol), len(self.contents))


class LeftClippedText(urwid.Text):
    def get_line_translation(
            self, maxcol: int, ta: Tuple[str, Any] = None) -> Any:
        if ta:
            text, _attr = ta
        else:
            text, _attr = self.get_text()
        return self.layout.layout(
            text, min(maxcol, len(text)), urwid.RIGHT, urwid.CLIP)


class Ui:
    def __init__(
            self,
            plugin: PluginBase,
            upload_settings: common.UploadSettings) -> None:
        self._plugin = plugin
        self._upload_settings = upload_settings
        self._undo_stack: List[Set[common.Tag]] = []
        self._running = True

        upload_settings.tags.on_update.append(self._on_tags_change)

        frame = urwid.Frame(None, header=self._make_header_widget())

        self._loop = urwid.MainLoop(
            frame,
            unhandled_input=self._keypress,
            event_loop=urwid.AsyncioEventLoop())
        self._loop.screen.set_terminal_properties(256)
        self._loop.screen.register_palette(_PALETTE)

        input_box = urwid.LineBox(
            FuzzyInput(plugin, self._loop), title='Tag input')
        urwid.connect_signal(
            input_box.original_widget, 'accept', self._on_tag_accept)

        self._chosen_tags_box = urwid.LineBox(
            ChosenTagsListBox(upload_settings.tags, plugin), title='')
        self._on_tags_change()

        self._columns = urwid.Columns([input_box, self._chosen_tags_box])
        self._columns.set_focus(0)
        frame.set_body(self._columns)

    async def add_from_user_input(self) -> None:
        self._loop.start()  # the loop is managed manually
        try:
            while self._running:
                await asyncio.sleep(0.1)
        finally:
            self._loop.stop()

    def _keypress(self, key: str) -> None:
        keymap = {
            'ctrl s': self._cycle_safety,
            'ctrl q': self._confirm,
            'ctrl x': self._toggle_focus,
            'ctrl r': self._undo_tag,
        }
        if key in keymap:
            keymap[key]()

    def _cycle_safety(self) -> None:
        self._upload_settings.safety = {
            Safety.Safe: Safety.Questionable,
            Safety.Questionable: Safety.Explicit,
            Safety.Explicit: Safety.Safe
        }[self._upload_settings.safety]
        self._loop.widget.set_header(self._make_header_widget())

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
            self._upload_settings.tags.delete(tag)
        self._chosen_tags_box.original_widget.schedule_update()

    def _on_tags_change(self) -> None:
        self._chosen_tags_box.set_title(
            'Chosen tags ({})'.format(len(self._upload_settings.tag_names)))

    def _on_tag_accept(self, _widget: urwid.Widget, text: str) -> None:
        text = common.unbox_from_ui(text)

        previous_tags = self._upload_settings.tags.get_all()
        self._upload_settings.tags.add(text, common.TagSource.UserInput)

        async def work() -> None:
            await self._chosen_tags_box.original_widget.update()

            async for implication in (
                    self._plugin.get_tag_implications(text)):
                self._upload_settings.tags.add(
                    implication, common.TagSource.Implication)
                await self._chosen_tags_box.original_widget.update()

            added_tags = set([
                tag
                for tag in self._upload_settings.tags.get_all()
                if tag not in previous_tags])
            self._undo_stack.append(added_tags)

        asyncio.ensure_future(work())

    def _make_header_widget(self) -> urwid.Widget:
        return urwid.Columns([
            (urwid.PACK, TableColumn([
                (urwid.Text('Path:')),
                (urwid.Text('Safety:')),
                (urwid.Text('Plugin:')),
            ])),
            TableColumn([
                LeftClippedText(str(self._upload_settings.path)),
                urwid.Text({
                    Safety.Safe: 'safe',
                    Safety.Questionable: 'questionable',
                    Safety.Explicit: 'explicit',
                }[self._upload_settings.safety]),
                urwid.Text(self._plugin.name),
            ])
        ], dividechars=1)


async def run(
        plugin: PluginBase, upload_settings: common.UploadSettings) -> None:
    with util.redirect_stdio():
        tagger = Ui(plugin, upload_settings)
        await tagger.add_from_user_input()
