import re
import typing as T

from bubblesub.fmt.ass.event import AssEvent
from bubblesub.fmt.ass.util import ass_to_plaintext

from .common import BaseResult, Violation


def check_double_words(event: AssEvent) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    for pair in re.finditer(r"(?<!\w)(\w+)\s+\1(?!\w)", text):
        word = pair.group(1)
        yield Violation(event, f"double word ({word})")
