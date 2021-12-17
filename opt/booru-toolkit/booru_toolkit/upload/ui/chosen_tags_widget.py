import asyncio

import urwid

from booru_toolkit.plugin import PluginBase
from booru_toolkit.upload import common
from booru_toolkit.upload.ui.ellipsis_text_layout import EllipsisTextLayout
from booru_toolkit.upload.ui.vim_list_box import VimListBox


class ChosenTagsListBox(VimListBox):
    def __init__(
        self, chosen_tags: common.TagList, plugin: PluginBase
    ) -> None:
        super().__init__(urwid.SimpleListWalker([]))
        self._chosen_tags = chosen_tags
        self._plugin = plugin
        self.schedule_update()

    def keypress(self, size: tuple[int, int], key: str) -> str | None:
        keymap = {"d": self._delete_selected, "delete": self._delete_selected}
        if key in keymap:
            keymap[key]()
            self._cancel_num()
            return None
        return super().keypress(size, key)

    def schedule_update(self) -> None:
        asyncio.ensure_future(self.update())

    async def update(self) -> None:
        new_list: list[urwid.Widget] = []
        for tag in self._chosen_tags.get_all():
            if tag.source == common.TagSource.Implication:
                attr_name = "implied-tag"
            elif tag.source == common.TagSource.Initial:
                attr_name = "initial-tag"
            elif not await self._plugin.tag_exists(tag.name):
                attr_name = "new-tag"
            else:
                attr_name = "tag"
            tag_usage_count = await self._plugin.get_tag_usage_count(tag.name)

            columns_widget = urwid.Columns(
                [
                    (
                        urwid.Text(
                            common.box_to_ui(tag.name),
                            align=urwid.LEFT,
                            wrap=urwid.CLIP,
                            layout=EllipsisTextLayout(),
                        )
                    ),
                    (urwid.PACK, urwid.Text(str(tag_usage_count))),
                ],
                dividechars=1,
            )
            setattr(columns_widget, "tag", tag)
            new_list.append(
                urwid.AttrWrap(columns_widget, attr_name, "f-" + attr_name)
            )
        list.clear(self.body)
        self.body.extend(new_list)

    def focus_tag(self, tag_name: str) -> None:
        for i, widget in enumerate(self.body):
            if widget.contents[0][0].text == tag_name:
                self._focus = i

    def _delete_selected(self) -> None:
        old_focused_item = self._focus
        self._chosen_tags.delete(self.body.get_focus()[0].tag)
        self.schedule_update()
        self._focus = old_focused_item
        self._invalidate()
