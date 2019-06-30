import re
import typing as T

from bubblesub.fmt.ass.event import AssEvent
from bubblesub.fmt.ass.util import ass_to_plaintext

from .common import (
    WORDS_WITH_PERIOD,
    BaseResult,
    Violation,
    get_next_non_empty_event,
    get_prev_non_empty_event,
    is_event_dialog,
)


def check_line_continuation(event: AssEvent) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    prev_event = get_prev_non_empty_event(event)
    next_event = get_next_non_empty_event(event)
    next_text = ass_to_plaintext(next_event.text) if next_event else ""
    prev_text = ass_to_plaintext(prev_event.text) if prev_event else ""

    if text.endswith("…") and next_text.startswith("…"):
        yield Violation([event, next_event], "old-style line continuation")

    if (
        re.search(r"\A[a-z]", text, flags=re.M)
        and is_event_dialog(event)
        and not re.search(r"[,:a-z]\Z", prev_text, flags=re.M)
        and not any(prev_text.endswith(word) for word in WORDS_WITH_PERIOD)
    ):
        yield Violation(event, "sentence begins with a lowercase letter")

    if not event.is_comment and is_event_dialog(event):
        if re.search(r"[,:a-z]\Z", text, flags=re.M) and not re.search(
            r'\A(I\s|I\'m|[a-z]|"[A-Z])', next_text, flags=re.M
        ):
            yield Violation(event, "possibly unended sentence")
