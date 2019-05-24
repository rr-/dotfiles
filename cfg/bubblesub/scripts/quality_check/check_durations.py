import typing as T

from bubblesub.ass.event import AssEvent
from bubblesub.ass.util import ass_to_plaintext, character_count

from .common import (
    BaseResult,
    Violation,
    get_next_non_empty_event,
    is_event_karaoke,
)

MIN_DURATION = 250  # milliseconds
MIN_DURATION_LONG = 500  # milliseconds
MIN_GAP = 250  # milliseconds


def check_durations(event: AssEvent) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)
    if not text or event.is_comment:
        return

    if event.duration < MIN_DURATION_LONG and character_count(text) >= 8:
        yield Violation(event, f"duration shorter than {MIN_DURATION_LONG} ms")

    elif event.duration < MIN_DURATION:
        yield Violation(event, f"duration shorter than {MIN_DURATION} ms")

    next_event = get_next_non_empty_event(event)

    if next_event and not (
        is_event_karaoke(next_event) and is_event_karaoke(event)
    ):
        gap = next_event.start - event.end
        if 0 < gap < MIN_GAP:
            yield Violation(
                [event, next_event],
                f"gap shorter than {MIN_GAP} ms ({gap} ms)",
            )
