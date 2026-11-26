"""Unified diffs, and the commits around them, parsed into a model."""

import dataclasses as dc
import re
import textwrap
from datetime import datetime, timezone


@dc.dataclass
class Line:
    kind: str  # one of " +-\\", or "~" for lines we could not parse
    text: str
    old: int | None
    new: int | None
    anchor: int  # the new-file line this sits at, for jumping to an editor


@dc.dataclass
class Hunk:
    header: str
    new_start: int
    lines: list[Line] = dc.field(default_factory=list)


@dc.dataclass
class FileDiff:
    old_path: str | None
    new_path: str | None
    status: str = "M"
    meta: list[str] = dc.field(default_factory=list)
    hunks: list[Hunk] = dc.field(default_factory=list)
    added: int = 0
    deleted: int = 0
    binary: bool = False
    commit: int = -1  # index into the commits, -1 for a bare diff
    blobs: tuple[str, str] | None = None  # from the index line
    whole: bool = False  # a whole file, as a tree shows it, not a diff

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or "?"

    @property
    def label(self) -> str:
        if self.status in "RC" and self.old_path != self.new_path:
            return f"{self.old_path} → {self.new_path}"
        return self.path


@dc.dataclass
class Commit:
    """Whatever came before a commit's diff: the header and the message."""

    lines: list[str]
    sha: str = ""
    refs: str = ""
    author: str = ""
    date: str = ""
    headers: list[str] = dc.field(default_factory=list)
    message: list[str] = dc.field(default_factory=list)
    extra: list[str] = dc.field(default_factory=list)
    unit: str = ""  # what this is when it is no commit, such as "tree"

    def __post_init__(self) -> None:
        for line in self.lines:
            commit = re.match(r"commit ([0-9a-f]{7,})(?: \((.*)\))?$", line)
            author = re.match(r"Author:\s*(.*?)(?:\s+<[^>]*>)?$", line)
            if commit and not self.sha:
                self.sha, self.refs = commit[1], commit[2] or ""
            elif author and not self.author:
                self.author = author[1]
            elif line.startswith("Date:") and self.author and not self.date:
                self.date = line[5:].strip()
            elif line.startswith("    ") or (self.message and not line):
                self.message.append(line[4:])
            elif line.strip():
                (self.extra if self.message else self.headers).append(line)
        self.message = trim_blank(self.message)

    @property
    def subject(self) -> str:
        return self.message[0].strip() if self.message else ""

    @property
    def key(self) -> str:
        """What the review file calls this: a commit's title, or unit:tree
        and the like for what is no commit."""
        return f"unit:{self.unit}" if self.unit else self.subject

    @property
    def title(self) -> str:
        return (
            " ".join(filter(None, [self.sha[:7], self.subject]))
            or (self.lines[0])
        )


def relative_date(text: str) -> str:
    """A git date, or an ISO one, as "2 hours ago"."""
    for fmt in ("%a %b %d %H:%M:%S %Y %z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            when = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue
    else:
        return text
    secs = (datetime.now(timezone.utc) - when).total_seconds()
    for unit, size in (
        ("year", 31557600),
        ("month", 2629800),
        ("week", 604800),
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
    ):
        if secs >= size:
            n = int(secs // size)
            return f"{n} {unit}{'s' if n > 1 else ''} ago"
    return "just now"


TRAILER_RE = re.compile(r"[\w-]+: \S")


def wrap(line: str, width: int) -> list[str]:
    """Wrap a message line, keeping list items hanging under their text."""
    if len(line) <= width:
        return [line]
    hang = re.match(r"\s*(?:[-*] |\d+[.)] )?", line).end()
    return textwrap.wrap(
        line,
        width,
        subsequent_indent=" " * hang,
        break_on_hyphens=False,
    ) or [line]


def trim_blank(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


COMMIT_RE = re.compile(r"commit (?:[0-9a-f]{7,}|-)( |$)")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@ ?(.*)$")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
INDEX_RE = re.compile(r"^index ([0-9a-f]+)\.\.([0-9a-f]+)\b")
PREFIX_RE = re.compile(r"^[abciow12]/")
C_ESCAPES = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13}


def unquote(path: str) -> str:
    if not (len(path) >= 2 and path[0] == path[-1] == '"'):
        return path
    body = path[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            if nxt in "01234567":
                out.append(int(body[i + 1 : i + 4], 8) & 0xFF)
                i += 4
                continue
            out.append(C_ESCAPES.get(nxt, ord(nxt)))
            i += 2
            continue
        out += body[i].encode()
        i += 1
    return out.decode(errors="replace")


def clean_path(path: str) -> str | None:
    path = unquote(path.rstrip("\t"))
    if path == "/dev/null":
        return None
    return PREFIX_RE.sub("", path, count=1)


def split_git_header(rest: str) -> tuple[str | None, str | None]:
    """Paths from `diff --git a/x b/y`, for when no ---/+++ lines follow."""
    if rest.startswith('"'):
        m = re.match(r'("(?:[^"\\]|\\.)*") (.*)$', rest)
        if m:
            return clean_path(m[1]), clean_path(m[2])
    half = (len(rest) - 1) // 2
    if len(rest) % 2 and rest[half] == " ":
        a, b = rest[:half], rest[half + 1 :]
        if clean_path(a) == clean_path(b):
            return clean_path(a), clean_path(b)
    a, sep, b = rest.partition(" b/")
    if sep:
        return clean_path(a), clean_path("b/" + b)
    return clean_path(rest), clean_path(rest)


def parse_diff(text: str) -> tuple[list[FileDiff], list[Commit]]:
    files: list[FileDiff] = []
    commits: list[Commit] = []
    preamble: list[str] = []
    cur: FileDiff | None = None
    hunk: Hunk | None = None
    state = "between"  # "header", "hunk", "raw" or "between"
    old_left = new_left = 0
    old_no = new_no = 0

    def add_commits(lines: list[str]) -> None:
        # git log shows a commit without changes as a header with no diff,
        # so a stretch of text can hold several commits.
        chunk: list[str] = []
        for line in lines + ["commit -"]:
            if COMMIT_RE.match(line) and trim_blank(chunk):
                commits.append(Commit(trim_blank(chunk)))
                chunk = []
            chunk.append(line)

    def start_file(old: str | None, new: str | None) -> FileDiff:
        nonlocal preamble
        # Text between two files' diffs opens a new commit, as in git show.
        add_commits(preamble)
        preamble = []
        f = FileDiff(old, new, commit=len(commits) - 1)
        files.append(f)
        return f

    for line in text.split("\n"):
        if line.startswith("diff --git "):
            cur = start_file(*split_git_header(line[11:]))
            hunk, state = None, "header"
            continue
        if line.startswith(("diff --cc ", "diff --combined ")):
            path = clean_path(line.split(" ", 2)[2])
            cur = start_file(path, path)
            cur.meta.append("combined diff, shown as is")
            hunk = Hunk("", 1)
            cur.hunks.append(hunk)
            state = "raw"
            continue
        if cur is None:
            preamble.append(line)
            continue

        if state == "raw":
            hunk.lines.append(Line("~", line, None, None, 1))
            continue

        if state == "hunk":
            tag, body = (line[:1] or " "), line[1:]
            if tag == " ":
                hunk.lines.append(Line(" ", body, old_no, new_no, new_no))
                old_no, new_no = old_no + 1, new_no + 1
                old_left, new_left = old_left - 1, new_left - 1
            elif tag == "-":
                hunk.lines.append(Line("-", body, old_no, None, new_no))
                cur.deleted += 1
                old_no, old_left = old_no + 1, old_left - 1
            elif tag == "+":
                hunk.lines.append(Line("+", body, None, new_no, new_no))
                cur.added += 1
                new_no, new_left = new_no + 1, new_left - 1
            elif tag == "\\":
                hunk.lines.append(Line("\\", line, None, None, new_no))
            else:
                state = "between"
            if old_left <= 0 and new_left <= 0:
                state = "between"
            if state == "hunk" or tag in " -+\\":
                continue

        if line.startswith("\\") and hunk is not None:
            hunk.lines.append(Line("\\", line, None, None, new_no))
            continue

        m = HUNK_RE.match(line)
        if m:
            old_no, new_no = int(m[1]), int(m[3])
            old_left = int(m[2]) if m[2] is not None else 1
            new_left = int(m[4]) if m[4] is not None else 1
            hunk = Hunk(line, new_no)
            cur.hunks.append(hunk)
            state = "hunk" if old_left or new_left else "between"
            continue

        if state != "header":
            preamble.append(line)
            continue
        if line.startswith("--- "):
            cur.old_path = clean_path(line[4:])
        elif line.startswith("+++ "):
            cur.new_path = clean_path(line[4:])
        elif line.startswith("new file mode"):
            cur.status = "A"
        elif line.startswith("deleted file mode"):
            cur.status = "D"
        elif line.startswith(("rename from ", "copy from ")):
            cur.status = "R" if line[0] == "r" else "C"
            cur.old_path = unquote(line.split(" ", 2)[2])
        elif line.startswith(("rename to ", "copy to ")):
            cur.new_path = unquote(line.split(" ", 2)[2])
        elif m := INDEX_RE.match(line):
            cur.blobs = (m[1], m[2])
        elif line.startswith(("similarity index", "dissimilarity index")):
            cur.meta.append(line.replace(" index", ""))
        elif line.startswith("old mode "):
            cur.meta.append(f"mode {line[9:]}")
        elif line.startswith("new mode "):
            cur.meta[-1:] = [f"{(cur.meta or ['mode ?'])[-1]} → {line[9:]}"]
        elif line.startswith(("Binary files", "GIT binary patch")):
            cur.binary = True
            cur.meta.append("binary file differs")
            state = "between"

    for f in files:
        if f.old_path is None and f.status == "M":
            f.status = "A"
        if f.new_path is None and f.status == "M":
            f.status = "D"
        if not f.hunks and not f.meta:
            f.meta.append("no content changes")
    add_commits(preamble)
    return files, commits
