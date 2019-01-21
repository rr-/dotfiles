import typing as T
from collections import defaultdict
from pathlib import Path

import ass_tag_parser
import fontTools.ttLib as font_tools
from bubblesub.api import Api

TT_NAME_ID_FONT_FAMILY = 1
TT_NAME_ID_FULL_NAME = 4
TT_NAME_ID_TYPOGRAPHIC_FAMILY = 16
TT_PLATFORM_MICROSOFT = 3


class FontInfo:
    def __init__(self, font_path):
        font = font_tools.TTFont(font_path)

        self.names = []
        self.is_bold = bool(font["OS/2"].fsSelection & (1 << 5))
        self.is_italic = bool(font["OS/2"].fsSelection & 1)
        self.glyphs = set(
            chr(y[0]) for x in font["cmap"].tables for y in x.cmap.items()
        )

        for record in font["name"].names:
            if record.platformID != TT_PLATFORM_MICROSOFT:
                continue

            if record.nameID not in {
                TT_NAME_ID_FONT_FAMILY,
                TT_NAME_ID_FULL_NAME,
                TT_NAME_ID_TYPOGRAPHIC_FAMILY,
            }:
                continue

            self.names.append(record.string.decode("utf-16-be"))


def get_used_font_styles(
    api: Api
) -> T.Dict[T.Tuple[str, bool, bool], T.Set[str]]:
    results = defaultdict(set)

    styles = {style.name: style for style in api.subs.styles}
    for line in api.subs.events:
        if line.is_comment:
            continue

        if line.style not in styles:
            continue

        family = styles[line.style].font_name
        is_bold = styles[line.style].bold
        is_italic = styles[line.style].italic

        try:
            ass_line = ass_tag_parser.parse_ass(line.text)
        except ass_tag_parser.ParseError:
            # ASS parsing errors are handled elsewhere
            continue

        for item in ass_line:
            if isinstance(item, ass_tag_parser.AssTagBold):
                is_bold = (
                    item.enabled if item.weight is None else item.weight > 100
                )
            elif isinstance(item, ass_tag_parser.AssTagItalic):
                is_italic = item.enabled
            elif isinstance(item, ass_tag_parser.AssTagFontName):
                family = (
                    item.name if item.name else styles[line.style].font_name
                )
            elif isinstance(item, ass_tag_parser.AssText):
                for glyph in item.text:
                    results[(family, is_bold, is_italic)].add(glyph)

    return results


def get_font_description(
    font_family: str, is_bold: bool, is_italic: bool
) -> str:
    attrs = []
    if is_bold:
        attrs.append("bold")
    if is_italic:
        attrs.append("italic")
    if attrs:
        return f"{font_family} ({', '.join(attrs)})"
    return font_family


def get_fonts(api) -> T.Dict[Path, FontInfo]:
    if not api.subs.path:
        return {}

    return {
        path: FontInfo(path)
        for path in (api.subs.path.parent / "../../oc-fonts").iterdir()
        if path.is_file()
    }


def locate_font(
    fonts: T.Dict[Path, FontInfo], family: str, is_bold: bool, is_italic: bool
) -> T.Optional[Path]:
    candidates = []
    for font_path, font in fonts.items():
        if family.lower() in [n.lower() for n in font.names]:
            weight = (font.is_bold == is_bold) + (font.is_italic == is_italic)
            candidates.append((weight, font_path, font))
    candidates.sort(key=lambda i: -i[0])
    if not candidates:
        return None
    return candidates[0]


def check_fonts(api: Api) -> None:
    api.log.info("Fonts summary:")

    results = get_used_font_styles(api)
    fonts = get_fonts(api)
    for font_specs, glyphs in results.items():
        font_family, is_bold, is_italic = font_specs
        api.log.info(
            f"– {get_font_description(*font_specs)}, {len(glyphs)} glyphs"
        )

        result = locate_font(fonts, font_family, is_bold, is_italic)
        if not result:
            api.log.warn(f"  font file not found")
            continue

        _weight, _font_path, font = result
        missing_glyphs = set()
        for glyph in glyphs:
            if glyph not in font.glyphs:
                missing_glyphs.add(glyph)

        if missing_glyphs:
            api.log.warn(f'  missing glyphs: {"".join(missing_glyphs)}')
