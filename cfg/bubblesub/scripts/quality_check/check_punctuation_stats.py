from collections import defaultdict

from bubblesub.api import Api
from bubblesub.fmt.ass.util import ass_to_plaintext

from .common import is_event_karaoke, is_event_title

CHARS = "!…"


def check_punctuation_stats(api: Api) -> None:
    stats = defaultdict(int)
    for event in api.subs.events:
        if is_event_title(event) or is_event_karaoke(event):
            continue
        for char in CHARS:
            stats[char] += ass_to_plaintext(event.text).count(char)

    api.log.info(
        "Punctuation stats: "
        + ", ".join(f"{char}: {count}" for char, count in stats.items())
    )
