import typing as T

from bubblesub.fmt.ass.event import AssEvent
from bubblesub.fmt.ass.style import AssStyleList

from .common import BaseResult, Violation


def check_style_validity(
    event: AssEvent, styles: AssStyleList
) -> T.Iterable[BaseResult]:
    if (
        event.style.startswith("[")
        and event.style.endswith("]")
        and event.is_comment
    ):
        return

    style = styles.get_by_name(event.style)
    if style is None:
        yield Violation(event, f"using non-existing style")
