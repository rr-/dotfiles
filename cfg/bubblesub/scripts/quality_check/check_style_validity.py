import typing as T

from bubblesub.ass.event import Event
from bubblesub.ass.style import StyleList

from .common import BaseResult, Violation


def check_style_validity(
    event: Event, styles: StyleList
) -> T.Iterable[BaseResult]:
    style = styles.get_by_name(event.style)
    if style is None:
        yield Violation(event, f"using non-existing style")
