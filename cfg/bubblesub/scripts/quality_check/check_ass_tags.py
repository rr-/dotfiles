import typing as T

from ass_tag_parser import (
    AssTagAlignment,
    AssTagComment,
    AssTagKaraoke,
    AssTagListEnding,
    AssTagListOpening,
    ParseError,
    parse_ass,
)
from bubblesub.fmt.ass.event import AssEvent

from .common import BaseResult, Violation


def get(source: T.List[T.Any], idx: int) -> T.Any:
    if idx < 0 or idx >= len(source):
        return None
    return source[idx]


def check_ass_tags(event: AssEvent) -> T.Iterable[BaseResult]:
    try:
        ass_line = parse_ass(event.text)
    except ParseError as ex:
        yield Violation(event, f"invalid syntax ({ex})")
        return

    for i, item in enumerate(ass_line):
        if (
            isinstance(item, AssTagListOpening)
            and isinstance(get(ass_line, i - 1), AssTagListEnding)
            and not isinstance(get(ass_line, i - 2), AssTagKaraoke)
        ):
            yield Violation(event, "disjointed tags")

        if isinstance(item, AssTagListEnding) and isinstance(
            get(ass_line, i - 1), AssTagListOpening
        ):
            yield Violation(event, "pointless tag")

    for item in ass_line:
        if isinstance(item, AssTagAlignment) and item.legacy:
            yield Violation(event, "using legacy alignment tag")

        elif isinstance(item, AssTagComment):
            yield Violation(event, "use notes to make comments")
