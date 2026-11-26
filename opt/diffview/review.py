"""Review comments and approvals, kept in one JSONL file per repository.

The file is `review.jsonl` in the repository's common .git directory, so
every worktree shares it. Each line is one JSON record:

    {"id": "a1b2c3", "author": "me", "text": "...", "created": "<iso>",
     "reply_to": null, "status": "open",
     "commit_title": "Add font cells",
     "path": "src/x.c", "side": "new", "line_text": "    foo();",
     "before": ["..."], "after": ["..."], "hunk": "int main(void)",
     "line": 42}

A thread is a comment with no `reply_to`, and its replies. Only the root's
`status` counts: "open", "resolved" or "deleted". A line with an `id` seen
before updates the fields it names, so resolving a thread is one more line:

    {"id": "a1b2c3", "status": "resolved"}

A comment with no `path` is about the whole commit. Comments find their
line again by `commit_title`, `path`, `side` and `line_text`, with `before`,
`after`, `hunk` and `line` to choose between equal lines, so they survive a
rebase. One whose line is gone is outdated, and shows on its commit's page.

An approval is a record of its own, the last one per title winning:

    {"type": "approval", "commit_title": "Add font cells", "approved": true}
"""

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from .model import Commit, FileDiff, Hunk, Line

REVIEW_FILE = "review.jsonl"
ANCHOR_CONTEXT = 3
HUNK_FUNC_SCORE = 5
CONTEXT_SCORE = 10


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Review:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.load()

    def load(self) -> None:
        self.comments: dict[str, dict] = {}
        self.approvals: dict[str, bool] = {}
        self.bad = 0
        try:
            text = self.path.read_text()
        except FileNotFoundError:
            return
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                self.bad += 1
                continue
            if not self.apply(rec):
                self.bad += 1

    def apply(self, rec: object) -> bool:
        if not isinstance(rec, dict):
            return False
        if rec.get("type") == "approval":
            title = rec.get("commit_title")
            if not isinstance(title, str):
                return False
            self.approvals[title] = bool(rec.get("approved"))
            return True
        if not isinstance(rec.get("id"), str):
            return False
        self.comments.setdefault(rec["id"], {}).update(rec)
        return True

    def append(self, rec: dict) -> None:
        with self.path.open("a") as handle:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.apply(rec)

    def add(self, author: str, text: str, **fields) -> str:
        cid = secrets.token_hex(3)
        while cid in self.comments:
            cid = secrets.token_hex(3)
        rec = {
            "id": cid,
            "author": author,
            "text": text,
            "created": now_iso(),
            "reply_to": None,
        }
        if fields.get("reply_to") is None:
            rec["status"] = "open"
        self.append(rec | fields)
        return cid

    def update(self, cid: str, **fields) -> None:
        self.append({"id": cid, **fields})

    def approve(self, title: str, approved: bool) -> None:
        self.append(
            {
                "type": "approval",
                "commit_title": title,
                "approved": approved,
                "created": now_iso(),
            }
        )

    def root(self, cid: str) -> str:
        """The thread a comment belongs to, through replies to replies."""
        seen = set()
        while cid not in seen:
            seen.add(cid)
            parent = self.comments.get(cid, {}).get("reply_to")
            if not parent or parent not in self.comments:
                return cid
            cid = parent
        return cid

    def threads(self) -> list[dict]:
        roots = [
            c
            for cid, c in self.comments.items()
            if self.root(cid) == cid and c.get("status") != "deleted"
        ]
        return sorted(roots, key=lambda c: str(c.get("created", "")))

    def replies(self, rid: str) -> list[dict]:
        found = [
            c
            for cid, c in self.comments.items()
            if cid != rid
            and self.root(cid) == rid
            and c.get("status") != "deleted"
        ]
        return sorted(found, key=lambda c: str(c.get("created", "")))

    def is_open(self, rid: str) -> bool:
        return self.comments.get(rid, {}).get("status", "open") == "open"


def side_lines(hunk: Hunk, side: str) -> list[tuple[int, Line]]:
    """A hunk's lines as one side of the diff reads them."""
    kinds = " -" if side == "old" else " +"
    return [(li, ln) for li, ln in enumerate(hunk.lines) if ln.kind in kinds]


def hunk_func(hunk: Hunk) -> str:
    """The function name git puts after a hunk header's second @@."""
    _, _, rest = hunk.header.partition(" @@")
    return rest.strip()


def can_anchor(line: Line) -> bool:
    return line.kind in " +-"


def make_anchor(f: FileDiff, hi: int, li: int) -> dict:
    hunk = f.hunks[hi]
    line = hunk.lines[li]
    side = "old" if line.kind == "-" else "new"
    same = [ln for _, ln in side_lines(hunk, side)]
    at = next(i for i, ln in enumerate(same) if ln is line)
    return {
        "path": (f.old_path if side == "old" else f.new_path) or f.path,
        "side": side,
        "line_text": line.text,
        "before": [ln.text for ln in same[max(0, at - ANCHOR_CONTEXT) : at]],
        "after": [ln.text for ln in same[at + 1 : at + 1 + ANCHOR_CONTEXT]],
        "hunk": hunk_func(hunk),
        "line": line.old if side == "old" else line.new,
    }


def commits_titled(commits: list[Commit], title: object) -> list[int]:
    return [ci for ci, c in enumerate(commits) if c.subject == title]


def place(c: dict, files: list[FileDiff], commits: list[Commit]) -> tuple:
    """Where a thread's root sits in this diff now.

    ("line", fi, hi, li), ("commit", ci), ("outdated", ci), or
    ("elsewhere",) when no commit in the range has its title.
    """
    cis = commits_titled(commits, c.get("commit_title"))
    if not cis:
        return ("elsewhere",)
    path = c.get("path")
    if not path:
        return ("commit", cis[0])
    side = "old" if c.get("side") == "old" else "new"
    text = c.get("line_text")
    before = list(c.get("before") or [])
    after = list(c.get("after") or [])
    hint = c.get("line") if isinstance(c.get("line"), int) else 0
    best: tuple | None = None
    best_score = 0.0
    for fi, f in enumerate(files):
        if f.commit not in cis or path not in (f.old_path, f.new_path):
            continue
        for hi, hunk in enumerate(f.hunks):
            same = side_lines(hunk, side)
            for at, (li, line) in enumerate(same):
                if line.text != text:
                    continue
                near = [ln.text for _, ln in same[:at]][::-1]
                far = [ln.text for _, ln in same[at + 1 :]]
                score = CONTEXT_SCORE * (
                    sum(a == b for a, b in zip(near, before[::-1]))
                    + sum(a == b for a, b in zip(far, after))
                )
                if hunk_func(hunk) == c.get("hunk"):
                    score += HUNK_FUNC_SCORE
                number = (line.old if side == "old" else line.new) or 0
                score -= abs(number - hint) / 1e6
                if best is None or score > best_score:
                    best, best_score = (fi, hi, li), score
    if best is None:
        return ("outdated", cis[0])
    return ("line", *best)
