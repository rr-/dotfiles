import asyncio
from typing import Optional, Tuple, Set, List
import urwid
from booru_toolkit.plugin import PluginBase
from booru_toolkit.plugin import Safety
from booru_toolkit.upload import common
from booru_toolkit.upload.ui.fuzzy_input_widget import FuzzyInput
from booru_toolkit.upload.ui.chosen_tags_widget import ChosenTagsListBox
from booru_toolkit.upload.ui.ellipsis_text_layout import EllipsisTextLayout


_PALETTE = [
    ('match', 'default', 'default'),
    ('e-match', 'light gray', 'default'),
    ('f-match', 'light green', 'default'),
    ('f-e-match', 'light green', 'default'),
    ('tag', 'default', 'default', None, None, None),
    ('new-tag', 'light red', 'default', None, 'h229', 'h202'),
    ('implied-tag', 'light green', 'default', None, None, 'h22'),
    ('initial-tag', 'dark blue', 'default', None, 'h255', 'h25'),
    ('f-tag', 'black', 'white', None, 'h255', 'h235'),
    ('f-new-tag', 'black', 'white', None, 'h255', 'h235'),
    ('f-implied-tag', 'black', 'white', None, 'h255', 'h235'),
    ('f-initial-tag', 'black', 'white', None, 'h255', 'h235'),
]


class TableColumn(urwid.Pile):
    def pack(
        self, size: Tuple[int, int], focus: bool = False
    ) -> Tuple[int, int]:
        maxcol = size[0]
        maximum = max([i[0].pack((maxcol,), focus)[0] for i in self.contents])
        return (min(maximum, maxcol), len(self.contents))


class Ui:
    def __init__(
        self, plugin: PluginBase, upload_settings: common.UploadSettings
    ) -> None:
        self._plugin = plugin
        self._upload_settings = upload_settings
        self._undo_stack: List[Set[common.Tag]] = []
        self._running = True

        upload_settings.tags.on_update.append(self._on_tags_change)

        frame = urwid.Frame(None, header=self._make_header_widget())

        self._loop = urwid.MainLoop(
            frame,
            unhandled_input=self._keypress,
            event_loop=urwid.AsyncioEventLoop(),
        )
        self._loop.screen.set_terminal_properties(256)
        self._loop.screen.register_palette(_PALETTE)

        input_box = urwid.LineBox(
            FuzzyInput(
                plugin, self._loop, self._upload_settings.tags.contains
            ),
            title='Tag input',
        )
        urwid.connect_signal(
            input_box.original_widget, 'accept', self._on_tag_accept
        )

        self._chosen_tags_box = urwid.LineBox(
            ChosenTagsListBox(upload_settings.tags, plugin), title=''
        )
        self._on_tags_change()

        self._columns = urwid.Columns([input_box, self._chosen_tags_box])
        self._columns.set_focus(0)
        frame.set_body(self._columns)

    def show_alert(self, message: str) -> None:
        original_widget = self._loop.widget

        def button_click(*args) -> None:
            self._loop.widget = original_widget

        button = urwid.Button('OK')
        urwid.connect_signal(button, 'click', button_click)

        self._loop.widget = urwid.Overlay(
            urwid.LineBox(urwid.Pile([urwid.Text(message), button])),
            original_widget,
            'center',
            (urwid.RELATIVE, 40),
            'middle',
            (urwid.PACK),
        )

    async def add_from_user_input(self) -> None:
        self._loop.start()  # the loop is managed manually
        try:
            while self._running:
                await asyncio.sleep(0.1)
        finally:
            self._loop.stop()

    def _keypress(self, key: str) -> None:
        keymap = {
            'meta i': self._cycle_anonymity,
            'meta s': self._cycle_safety,
            'ctrl q': self._confirm,
            'ctrl x': self._toggle_focus,
            'ctrl r': self._undo_tag,
        }
        if key in keymap:
            keymap[key]()

    def _cycle_anonymity(self) -> None:
        self._upload_settings.anonymous = not self._upload_settings.anonymous
        self._loop.widget.set_header(self._make_header_widget())

    def _cycle_safety(self) -> None:
        self._upload_settings.safety = {
            Safety.Safe: Safety.Questionable,
            Safety.Questionable: Safety.Explicit,
            Safety.Explicit: Safety.Safe,
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
            'Chosen tags ({})'.format(len(self._upload_settings.tag_names))
        )

    def _on_tag_accept(self, _widget: urwid.Widget, text: str) -> None:
        text = common.unbox_from_ui(text)

        async def work() -> None:
            tag_name = await self._plugin.get_tag_real_name(text) or text

            previous_tags = self._upload_settings.tags.get_all()
            self._upload_settings.tags.add(
                tag_name, common.TagSource.UserInput
            )

            await self._chosen_tags_box.original_widget.update()

            async for implication in (
                self._plugin.get_tag_implications(tag_name)
            ):
                self._upload_settings.tags.add(
                    implication, common.TagSource.Implication
                )
                await self._chosen_tags_box.original_widget.update()

            self._chosen_tags_box.original_widget.focus_tag(tag_name)

            added_tags = set(
                [
                    tag
                    for tag in self._upload_settings.tags.get_all()
                    if tag not in previous_tags
                ]
            )
            self._undo_stack.append(added_tags)

        asyncio.ensure_future(work())

    def _make_header_widget(self) -> urwid.Widget:
        return urwid.Columns(
            [
                (
                    urwid.PACK,
                    TableColumn(
                        [
                            (urwid.Text('Plugin:')),
                            (urwid.Text('Anonymity:')),
                            (urwid.Text('Safety:')),
                            (urwid.Text('Path:')),
                        ]
                    ),
                ),
                TableColumn(
                    [
                        urwid.Text(self._plugin.name),
                        urwid.Text(
                            {False: 'off', True: 'on'}[
                                self._upload_settings.anonymous
                            ]
                        ),
                        urwid.Text(
                            {
                                Safety.Safe: 'safe',
                                Safety.Questionable: 'questionable',
                                Safety.Explicit: 'explicit',
                            }[self._upload_settings.safety]
                        ),
                        urwid.Text(
                            str(self._upload_settings.path),
                            wrap=urwid.CLIP,
                            align=urwid.RIGHT,
                            layout=EllipsisTextLayout(),
                        ),
                    ]
                ),
            ],
            dividechars=1,
        )


async def run(
    plugin: PluginBase,
    upload_settings: common.UploadSettings,
    message: Optional[str],
) -> None:
    ui = Ui(plugin, upload_settings)
    if message:
        ui.show_alert(message)
    await ui.add_from_user_input()
