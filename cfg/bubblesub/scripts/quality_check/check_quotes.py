import re
import typing as T

from bubblesub.fmt.ass.event import AssEvent
from bubblesub.fmt.ass.util import ass_to_plaintext

from .common import BaseResult, DebugInformation, Information, Violation


def check_quotes(event: AssEvent) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    if text.count('"') == 1:
        yield Information(event, "partial quote")
        return

    if re.search('".+[:,]"', text):
        yield Violation(event, "punctuation inside quotation marks")

    if re.search(r'".+"[\.,…?!]', text, flags=re.M):
        yield DebugInformation(event, "punctuation outside quotation marks")

    if re.search(r'[a-z]\s".+[\.…?!]"', text, flags=re.M):
        yield Violation(event, "punctuation inside quotation marks")
    elif re.search(r'".+[\.…?!]"', text, flags=re.M):
        yield DebugInformation(event, "punctuation inside quotation marks")
