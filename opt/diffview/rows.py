"""The rows of the diff pane."""

import dataclasses as dc


@dc.dataclass
class Row:
    kind: str  # "file", "meta", "hunk", "line", "commit" or "note"
    file: int
    hunk: int = 0
    line: int = 0
    text: str = ""
    tone: str = ""  # how a commit message row is drawn
    page: int = 0
    note: str = ""  # the comment a note row shows
    thread: str = ""  # and the thread it is in


class Quit(Exception):
    pass
