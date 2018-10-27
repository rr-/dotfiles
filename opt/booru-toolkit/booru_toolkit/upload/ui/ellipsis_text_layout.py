from typing import Any
import urwid


ELLIPSIS = '...'


class EllipsisTextLayout(urwid.TextLayout):
    def supports_align_mode(self, align: Any) -> bool:
        return align in (urwid.LEFT, urwid.RIGHT)

    def supports_wrap_mode(self, wrap: Any) -> bool:
        return wrap == urwid.CLIP

    def layout(self, text: str, width: int, align: Any, wrap: Any) -> Any:
        if urwid.util.calc_width(text, 0, len(text)) <= width:
            return [[(len(text), 0, len(text))]]

        if width <= len(ELLIPSIS):
            return [[(width, 1, b'.' * width)]]

        ellipsis_segment = (len(ELLIPSIS), 1, ELLIPSIS.encode('utf-8'))
        offset = 1
        if align == urwid.LEFT:
            while True:
                part = text[0 : len(text) - len(ELLIPSIS) - offset] + ELLIPSIS
                if urwid.util.calc_width(part, 0, len(part)) <= width:
                    break
                offset += 1
            text_segment = (
                len(text) - offset - len(ELLIPSIS),
                0,
                len(text) - offset - len(ELLIPSIS),
            )
            return [[text_segment, ellipsis_segment]]
        elif align == urwid.RIGHT:
            while True:
                part = ELLIPSIS + text[len(ELLIPSIS) + offset :]
                if urwid.util.calc_width(part, 0, len(part)) <= width:
                    break
                offset += 1
            text_segment = (
                len(text) - offset - len(ELLIPSIS),
                offset + len(ELLIPSIS),
                len(text),
            )
            return [[ellipsis_segment, text_segment]]
        else:
            assert False
