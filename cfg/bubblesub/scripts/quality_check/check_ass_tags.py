import typing as T

import ass_tag_parser
from bubblesub.ass.event import Event

from .common import BaseResult, Violation


def check_ass_tags(event: Event) -> T.Iterable[BaseResult]:
    try:
        ass_line = ass_tag_parser.parse_ass(event.text)
    except ass_tag_parser.ParseError as ex:
        yield Violation(event, f"invalid syntax ({ex})")
        return

    violations: T.List[Violation] = []

    def visitor(item: ass_tag_parser.AssItem) -> None:
        nonlocal violations

        if isinstance(item, ass_tag_parser.AssTagList) and not item.tags:
            violations.append(Violation(event, "pointless tag"))

        elif isinstance(item, ass_tag_parser.AssTagAlignment) and item.legacy:
            violations.append(Violation(event, "using legacy alignment tag"))

        elif isinstance(item, ass_tag_parser.AssTagComment):
            violations.append(Violation(event, "use notes to make comments"))

    ass_tag_parser.walk_ass_line(ass_line, visitor)

    yield from violations

    if "}{" in event.text:
        yield Violation(event, "disjointed tags")
