import re
import typing as T
from copy import copy

from bubblesub.api import Api
from bubblesub.ass_renderer import AssRenderer
from bubblesub.fmt.ass.event import AssEvent

from .common import (
    WIDTH_MULTIPLIERS,
    BaseResult,
    Information,
    get_width,
    is_event_title,
    measure_frame_size,
)


def check_unnecessary_breaks(
    event: AssEvent, api: Api, renderer: AssRenderer
) -> T.Iterable[BaseResult]:
    if r"\N" not in event.text:
        return
    event_copy = copy(event)
    event_copy.text = event.text.replace(r"\N", " ")
    width, _height = measure_frame_size(api, renderer, event_copy)
    optimal_width = get_width(api) * WIDTH_MULTIPLIERS[1]

    many_sentences = len(re.split(r"(?<=[\.!?…—] )", event_copy.text)) > 1
    if (
        width < optimal_width
        and not many_sentences
        and not is_event_title(event)
    ):
        yield Information(
            event,
            f"possibly unnecessary break "
            f"({optimal_width - width:.02f} until {optimal_width:.02f})",
        )
