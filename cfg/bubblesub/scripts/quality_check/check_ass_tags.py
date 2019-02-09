import typing as T

import ass_tag_parser
from bubblesub.ass.event import AssEvent

from .common import BaseResult, Violation


def check_ass_tags(event: AssEvent) -> T.Iterable[BaseResult]:
    try:
        ass_line = ass_tag_parser.parse_ass(event.text)
    except ass_tag_parser.ParseError as ex:
        yield Violation(event, f"invalid syntax ({ex})")
        return

    violations: T.List[Violation] = []
    opened = False
    closed = False

    for item in ass_line:
        if isinstance(item, ass_tag_parser.AssTagListOpening):
            opened = True
            if closed:
                violations.append(Violation(event, "disjointed tags"))
            closed = False
        elif isinstance(item, ass_tag_parser.AssTagListEnding):
            closed = True
            if opened:
                violations.append(Violation(event, "pointless tag"))
            opened = False
        else:
            opened = False
            closed = False

        if isinstance(item, ass_tag_parser.AssTagAlignment) and item.legacy:
            violations.append(Violation(event, "using legacy alignment tag"))

        elif isinstance(item, ass_tag_parser.AssTagComment):
            violations.append(Violation(event, "use notes to make comments"))

    yield from violations
