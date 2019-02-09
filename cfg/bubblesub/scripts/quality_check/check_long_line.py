import typing as T

from bubblesub.api import Api
from bubblesub.ass.event import AssEvent
from bubblesub.ui.ass_renderer import AssRenderer

from .common import (
    WIDTH_MULTIPLIERS,
    BaseResult,
    Violation,
    get_width,
    measure_frame_size,
)


def check_long_line(
    event: AssEvent,
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
