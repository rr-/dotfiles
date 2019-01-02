import argparse
import bisect
import re
import typing as T
from collections import defaultdict
from copy import copy

import ass_tag_parser
import enchant
import fontTools.ttLib as font_tools

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.api.log import LogLevel
from bubblesub.ass.event import Event, EventList
from bubblesub.ass.info import Metadata
from bubblesub.ass.style import StyleList
from bubblesub.ass.util import (
    ass_to_plaintext,
    character_count,
    spell_check_ass_line,
)
from bubblesub.opt.menu import MenuCommand
from bubblesub.ui.ass_renderer import AssRenderer

MIN_DURATION = 250  # milliseconds
MIN_DURATION_LONG = 500  # milliseconds
MIN_GAP = 250

NON_STUTTER_PREFIXES = {"half", "well"}
NON_STUTTER_SUFFIXES = {"kun", "san", "chan", "smaa", "senpai", "sensei"}
NON_STUTTER_WORDS = {"bye-bye", "part-time"}

SPELL_CHECK_LANGUAGE = "en_US"

WIDTH_MULTIPLIERS = {1: 0.6, 2: 0.9}


def _get_prev_non_empty_event(event: Event) -> T.Optional[Event]:
    event = event.prev
    while event:
        if ass_to_plaintext(event.text) and not event.is_comment:
            return event
        event = event.prev
    return None


def _get_next_non_empty_event(event: Event) -> T.Optional[Event]:
    event = event.next
    while event:
        if ass_to_plaintext(event.text) and not event.is_comment:
            return event
        event = event.next
    return None


class BaseResult:
    def __init__(
        self, event: T.Union[Event, T.List[Event]], text: str
    ) -> None:
        if isinstance(event, list):
            self.event = event[0]
            self.additional_events = event[1:]
        else:
            self.event = event
            self.additional_events = []
        self.text = text

    @property
    def events(self) -> T.Iterable[Event]:
        yield self.event
        yield from self.additional_events

    def __repr__(self) -> str:
        ids = "+".join([f'#{event.number or "?"}' for event in self.events])
        return f"{ids}: {self.text}"


class DebugInformation(BaseResult):
    log_level = LogLevel.Debug


class Information(BaseResult):
    log_level = LogLevel.Info


class Violation(BaseResult):
    log_level = LogLevel.Warning


def check_style_validity(
    event: Event, styles: StyleList
) -> T.Iterable[BaseResult]:
    style = styles.get_by_name(event.style)
    if style is None:
        yield Violation(event, f"using non-existing style")


def check_durations(event: Event) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)
    if not text or event.is_comment:
        return

    if event.duration < MIN_DURATION_LONG and character_count(text) >= 8:
        yield Violation(event, f"duration shorter than {MIN_DURATION_LONG} ms")

    elif event.duration < MIN_DURATION:
        yield Violation(event, f"duration shorter than {MIN_DURATION} ms")

    next_event = _get_next_non_empty_event(event)

    if next_event:
        gap = next_event.start - event.end
        if 0 < gap < MIN_GAP:
            yield Violation(
                [event, next_event],
                f"gap shorter than {MIN_GAP} ms ({gap} ms)",
            )


def check_punctuation(event: Event) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    if text.startswith("\n") or text.endswith("\n"):
        yield Violation(event, "extra line break")
    elif re.search(r"^\s|\s$", text):
        yield Violation(event, "extra whitespace")

    if text.count("\n") >= 2:
        yield Violation(event, "three or more lines")

    if re.search(r"\n\s|\s\n", text):
        yield Violation(event, "whitespace around line break")

    if re.search(r"\n[.,?!:;]", text):
        yield Violation(event, "line break before punctuation")
    elif re.search(r"\s[.,?!:;]", text):
        yield Violation(event, "whitespace before punctuation")

    if "  " in text:
        yield Violation(event, "double space")

    if "..." in text:
        yield Violation(event, "bad ellipsis (expected …)")
    elif re.search("[…,.!?:;][,.]", text):
        yield Violation(event, "extra comma or dot")

    context = re.split(r"\W+", re.sub('[.,?!"]', "", text.lower()))
    for word in {
        "im",
        "youre",
        "hes",
        "shes",
        "theyre",
        "isnt",
        "arent",
        "wasnt",
        "werent",
        "didnt",
        "thats",
        "heres",
        "theres",
        "wheres",
        "cant",
        "dont",
        "wouldnt",
        "couldnt",
        "shouldnt",
        "hasnt",
        "havent",
        "ive",
        "wouldve",
        "youve",
        "ive",
    }:
        if word in context:
            yield Violation(event, "missing apostrophe")

    if re.search("^– .* –$", text, flags=re.M):
        yield Violation(event, "bad dash (expected —)")
    elif not re.search("^—.*—$", text, flags=re.M):
        if len(re.findall(r"^–", text, flags=re.M)) == 1:
            yield Violation(event, "dialog with just one person")

        if re.search(r"[-–]$", text, flags=re.M):
            yield Violation(event, "bad dash (expected —)")

        if re.search(r"^- |^—", text, flags=re.M):
            yield Violation(event, "bad dash (expected –)")

        if re.search(r" - ", text, flags=re.M):
            yield Violation(event, "bad dash (expected –)")

    if re.search(r" —|— ", text):
        yield Violation(event, "whitespace around —")

    match = re.search(r"(\w+[\.!?])\s+[a-z]", text, flags=re.M)
    if match:
        if match.group(1) not in {"vs."}:
            yield Violation(event, "lowercase letter after sentence end")

    match = re.search(r"^([A-Z][a-z]{,3})-([a-z]+)", text, flags=re.M)
    if match:
        if (
            match.group(0).lower() not in NON_STUTTER_WORDS
            and match.group(1).lower() not in NON_STUTTER_PREFIXES
            and match.group(2).lower() not in NON_STUTTER_SUFFIXES
        ):
            yield Violation(event, "possibly wrong stutter capitalization")

    if re.search(r"[\.,?!:;][A-Za-z]|[a-zA-Z]…[A-Za-z]", text):
        yield Violation(event, "missing whitespace after punctuation mark")

    if re.search(
        "\\s|\N{ZERO WIDTH SPACE}", text.replace(" ", "").replace("\n", "")
    ):
        yield Violation(event, "unrecognized whitespace")


def check_quotes(event: Event) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    if text.count('"') == 1:
        yield Information(event, "partial quote")
        return

    if re.search('".+[:,]"', text):
        yield Violation(event, "punctuation inside quotation marks")

    if re.search(r'".+"[\.,…?!]', text, flags=re.M):
        yield DebugInformation(event, "punctuation outside quotation marks")

    if re.search(r'[a-z]\s".+[\.…?!]"', text, flags=re.M):
        yield Violation(event, "punctuation inside quotation marks")
    elif re.search(r'".+[\.…?!]"', text, flags=re.M):
        yield DebugInformation(event, "punctuation inside quotation marks")


def check_line_continuation(event: Event) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    prev_event = _get_prev_non_empty_event(event)
    next_event = _get_next_non_empty_event(event)
    next_text = ass_to_plaintext(next_event.text) if next_event else ""
    prev_text = ass_to_plaintext(prev_event.text) if prev_event else ""

    if text.endswith("…") and next_text.startswith("…"):
        yield Violation([event, next_event], "old-style line continuation")

    if (
        re.search(r"\A[a-z]", text, flags=re.M)
        and not re.search(r"[,:a-z]\Z", prev_text, flags=re.M)
        and not prev_text.endswith("vs.")
    ):
        yield Violation(event, "sentence begins with a lowercase letter")

    if (
        re.search(r"[,:a-z]\Z", text, flags=re.M)
        and not re.search(r"\A[a-z]", next_text, flags=re.M)
        and not re.search(r"\AI\s", next_text, flags=re.M)
    ):
        if (
            not event.is_comment
            and event.actor != "[karaoke]"
            and event.actor != "[title]"
            and event.actor != "(sign)"
        ):
            yield Violation(event, "possibly unended sentence")


def check_ass_tags(event: Event) -> T.Iterable[BaseResult]:
    try:
        result = ass_tag_parser.parse_ass(event.text)
    except ass_tag_parser.ParsingError as ex:
        yield Violation(event, f"invalid syntax ({ex})")
        return

    for item in result:
        if item["type"] != "tags":
            continue
        if not item["children"]:
            yield Violation(event, "pointless ASS tag")
        for subitem in item["children"]:
            if subitem["type"] == "alignment" and subitem["legacy"]:
                yield Violation(event, "using legacy alignment tag")
            if subitem["type"] == "comment":
                yield Violation(event, "use notes to make comments")
    if "}{" in event.text:
        yield Violation(event, "disjointed tags")


def check_double_words(event: Event) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    for pair in re.finditer(r"(?<!\w)(\w+)\s+\1(?!\w)", text):
        word = pair.group(1)
        yield Violation(event, f"double word ({word})")


def check_spelling(api):
    if not api.subs.path:
        return

    try:
        dictionary = enchant.DictWithPWL(
            SPELL_CHECK_LANGUAGE, pwl=str(api.subs.path.with_name("dict.txt"))
        )
    except enchant.errors.DictNotFoundError:
        api.log.warn(f'Dictionary "{SPELL_CHECK_LANGUAGE}" not found')
        return

    misspelling_map = defaultdict(set)
    for event in api.subs.events:
        if event.actor == "[karaoke]":
            continue
        text = ass_to_plaintext(event.text)
        for _start, _end, word in spell_check_ass_line(dictionary, text):
            misspelling_map[word].add(event.number)

    api.log.info("Misspelt words:")
    for word, line_numbers in sorted(
        misspelling_map.items(), key=lambda item: len(item[1]), reverse=True
    ):
        api.log.warn(
            f"- {word}: " + ", ".join(f"#{num}" for num in line_numbers)
        )


def check_actors(api):
    api.log.info("Actors summary:")
    actors = defaultdict(int)

    for line in api.subs.events:
        actors[line.actor] += 1

    for actor, occurrences in sorted(actors.items(), key=lambda kv: -kv[1]):
        api.log.info(f"– {occurrences} time(s): {actor}")


def check_styles(api):
    api.log.info("Styles summary:")
    styles = defaultdict(int)

    for line in api.subs.events:
        styles[line.style] += 1

    for style, occurrences in sorted(styles.items(), key=lambda kv: -kv[1]):
        api.log.info(f"– {occurrences} time(s): {style}")


def check_fonts(api):
    api.log.info("Fonts summary:")

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

    def get_used_font_styles(api):
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
                chunks = ass_tag_parser.parse_ass(line.text)
            except ass_tag_parser.ParsingError:
                # ASS parsing errors are handled elsewhere
                continue

            for chunk in chunks:
                if chunk["type"] == "tags":
                    for ass_tag in chunk["children"]:
                        if ass_tag["type"] == "bold":
                            if "enabled" in ass_tag:
                                is_bold = ass_tag["enabled"]
                            else:
                                is_bold = ass_tag["weight"] > 100
                        elif ass_tag["type"] == "italics":
                            is_italic = ass_tag["enabled"]
                        elif ass_tag["type"] == "font-name":
                            family = ass_tag["name"]
                elif chunk["type"] == "text":
                    for glyph in chunk["text"]:
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

    def get_fonts():
        if not api.subs.path:
            return {}

        return {
            path: FontInfo(path)
            for path in (api.subs.path.parent / "../../oc-fonts").iterdir()
            if path.is_file()
        }

    def locate_font(fonts, family, is_bold, is_italic):
        candidates = []
        for font_path, font in fonts.items():
            if family.lower() in [n.lower() for n in font.names]:
                weight = (font.is_bold == is_bold) + (
                    font.is_italic == is_italic
                )
                candidates.append((weight, font_path, font))
        candidates.sort(key=lambda i: -i[0])
        if not candidates:
            return None
        return candidates[0]

    results = get_used_font_styles(api)
    fonts = get_fonts()
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


def measure_frame_size(
    renderer: AssRenderer, event: Event
) -> T.Tuple[int, int]:
    fake_event_list = EventList()
    fake_event_list.append(copy(event))

    renderer.set_source(
        style_list=renderer.style_list,
        event_list=fake_event_list,
        info=renderer.info,
        video_resolution=renderer.video_resolution,
    )

    layers = list(renderer.render_raw(time=event.start))
    if not layers:
        return (0, 0)
    min_x = min(layer.dst_x for layer in layers)
    min_y = min(layer.dst_y for layer in layers)
    max_x = max(layer.dst_x + layer.w for layer in layers)
    max_y = max(layer.dst_y + layer.h for layer in layers)
    return (max_x - min_x, max_y - min_y)


def get_optimal_line_heights(
    api: Api, renderer: AssRenderer
) -> T.Dict[str, float]:
    TEST_LINE_COUNT = 20
    VIDEO_RES_X = 100
    VIDEO_RES_Y = TEST_LINE_COUNT * 300

    fake_info = Metadata()
    renderer.set_source(
        style_list=api.subs.styles,
        event_list=api.subs.events,
        info=fake_info,
        video_resolution=(VIDEO_RES_X, VIDEO_RES_Y),
    )

    ret = {}
    for style in api.subs.styles:
        event = Event(
            start=0,
            end=1000,
            text="\\N".join(["gjMW"] * TEST_LINE_COUNT),
            style=style.name,
        )

        _frame_width, frame_height = measure_frame_size(renderer, event)
        line_height = frame_height / TEST_LINE_COUNT
        ret[event.style] = line_height
        api.log.debug(f"average height for {event.style}: {line_height}")
    return ret


def get_height(api: Api) -> int:
    return int(api.subs.info.get("PlayResY"))


def get_width(api: Api) -> int:
    return int(get_height(api) * 4 / 3)


def check_unnecessary_breaks(
    event: Event,
    api: Api,
    renderer: AssRenderer,
    optimal_line_heights: T.Dict[str, float],
) -> T.Iterable[BaseResult]:
    if r"\N" not in event.text:
        return
    event_copy = copy(event)
    event_copy.text = event.text.replace(r"\N", " ")
    width, _height = measure_frame_size(renderer, event_copy)
    optimal_width = get_width(api) * WIDTH_MULTIPLIERS[1]
    if width < optimal_width and not "– " in event.text:
        yield Information(
            event,
            f"possibly unnecessary break "
            f"({optimal_width - width:.02f} until {optimal_width:.02f})",
        )


def check_long_line(
    event: Event,
    api: Api,
    renderer: AssRenderer,
    optimal_line_heights: T.Dict[str, float],
) -> T.Iterable[BaseResult]:
    width, height = measure_frame_size(renderer, event)
    average_height = optimal_line_heights.get(event.style, 0)
    line_count = round(height / average_height) if average_height else 0
    if not line_count:
        return

    try:
        width_multiplier = WIDTH_MULTIPLIERS[line_count]
    except LookupError:
        yield Violation(
            event, f"too many lines ({height}/{average_height} = {line_count})"
        )
    else:
        optimal_width = get_width(api) * width_multiplier
        if width > optimal_width:
            yield Violation(
                event,
                f"too long line "
                f"({width - optimal_width:.02f} beyond {optimal_width:.02f})",
            )


def list_violations(api: Api) -> T.Iterable[BaseResult]:
    renderer = AssRenderer()
    optimal_line_heights = get_optimal_line_heights(api, renderer)
    renderer.set_source(
        style_list=api.subs.styles,
        event_list=api.subs.events,
        info=api.subs.info,
        video_resolution=(get_width(api), get_height(api)),
    )

    for event in api.subs.events:
        yield from check_style_validity(event, api.subs.styles)
        yield from check_durations(event)
        yield from check_punctuation(event)
        yield from check_quotes(event)
        yield from check_line_continuation(event)
        yield from check_ass_tags(event)
        yield from check_double_words(event)
        yield from check_unnecessary_breaks(
            event, api, renderer, optimal_line_heights
        )
        yield from check_long_line(event, api, renderer, optimal_line_heights)


class QualityCheckCommand(BaseCommand):
    names = ["qc", "quality-check"]
    help_text = "Tries to pinpoint common issues with the subtitles."

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--focus-prev", action="store_true")
        parser.add_argument("-n", "--focus-next", action="store_true")

    async def run(self):
        if self.args.focus_prev or self.args.focus_next:
            violations = [
                result
                for result in list_violations(self.api)
                if result.log_level in {LogLevel.Warning, LogLevel.Error}
            ]
            violated_indexes = sorted(
                violation.event.index for violation in violations
            )

            if self.args.focus_prev:
                selected_index = self.api.subs.selected_indexes[0]
                next_index = violated_indexes[
                    bisect.bisect_left(violated_indexes, selected_index) - 1
                ]

            elif self.args.focus_next:
                selected_index = self.api.subs.selected_indexes[-1]
                next_index = violated_indexes[
                    bisect.bisect_right(violated_indexes, selected_index)
                    % len(violated_indexes)
                ]

            else:
                raise AssertionError

            self.api.subs.selected_indexes = [next_index]
            for result in violations:
                if result.event.index == next_index:
                    self.api.log.log(result.log_level, repr(result))
            return

        results = sorted(
            list_violations(self.api),
            key=lambda result: (
                re.match("^([^(]*).*?$", result.text).group(1),
                result.event.number,
            ),
        )
        for result in results:
            self.api.log.log(result.log_level, repr(result))

        check_spelling(self.api)
        check_actors(self.api)
        check_styles(self.api)
        check_fonts(self.api)


COMMANDS = [QualityCheckCommand]
MENU = [MenuCommand("&Quality check", "qc")]
