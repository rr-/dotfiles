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

A thread's root names the `branch` it was written on review of, and shows
only when that branch is reviewed, though another branch may have a
commit of the same title. One without a `branch` shows on every branch.

A comment with no `path` is about the whole commit, and one with a `path`
but no `line_text` about that whole file. Comments find their
line again by `commit_title`, `path`, `side` and `line_text`, with `before`,
`after`, `hunk` and `line` to choose between equal lines, so they survive a
rebase. One whose line is gone is outdated, and shows on its commit's page.

An approval is a record of its own, the last one per title winning:

    {"type": "approval", "commit_title": "Add font cells", "approved": true}

A commit is in one of three states: neutral, approved, or changes
requested. Changes requested is the same record with `changes_requested`
set, and means: do not turn this commit into a pull request yet.

    {"type": "approval", "commit_title": "Add font cells",
     "approved": false, "changes_requested": true}

Both false is neutral: an approval or a request taken back.

A file of a commit has a verdict of its own, in the same record with the
file's `path`. That marks how far the review got; the commit's own
verdict, the record without `path`, is what decides the pull request.

    {"type": "approval", "commit_title": "Add font cells",
     "path": "src/font.c", "approved": true, "changes_requested": false}
"""

import json
import os
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
    def __init__(self, path: Path, branch: str | None = None) -> None:
        self.path = path
        self.branch = branch  # new threads are about this branch only
        self.load()

    def load(self) -> None:
        self.comments: dict[str, dict] = {}
        self.approvals: dict[str, bool] = {}
        self.changes: dict[str, bool] = {}
        self.file_verdicts: dict[tuple[str, str], str] = {}
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
            title = rec_key(rec)
            if not isinstance(title, str):
                return False
            if path := rec.get("path"):
                verdict = ""
                if rec.get("approved"):
                    verdict = "approved"
                elif rec.get("changes_requested"):
                    verdict = "changes requested"
                self.file_verdicts[title, str(path)] = verdict
                return True
            self.approvals[title] = bool(rec.get("approved"))
            self.changes[title] = bool(rec.get("changes_requested"))
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
            if self.branch:
                rec["branch"] = self.branch
        self.append(rec | fields)
        return cid

    def update(self, cid: str, **fields) -> None:
        self.append({"id": cid, **fields})

    def approve(
        self,
        title: str,
        approved: bool,
        changes: bool = False,
        path: str | None = None,
    ) -> None:
        """A commit's verdict, or with path one of its files'."""
        rec = {"type": "approval", **key_fields(title)}
        if path:
            rec["path"] = path
        self.append(
            rec
            | {
                "approved": approved,
                "changes_requested": changes,
                "created": now_iso(),
            }
        )

    def file_verdict(self, title: str, path: str) -> str:
        return self.file_verdicts.get((title, path), "")

    def verdict(self, title: str) -> str:
        """ "approved", "changes requested", or "" for neutral."""
        if self.approvals.get(title):
            return "approved"
        if self.changes.get(title):
            return "changes requested"
        return ""

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

    def prune(self, done: set[str], keep: set[str]) -> tuple[int, int]:
        """Drop the threads and approvals of commits that have landed.

        A title in done and not in keep goes, with every reply to its
        threads. The file is written anew and renamed over the old one,
        unless something appended to it meanwhile: then it is read again.
        Gives how many threads and approvals went.
        """
        gone = done - keep
        for _ in range(5):
            try:
                seen = self.path.stat()
            except FileNotFoundError:
                return 0, 0
            self.load()
            roots = {
                cid
                for cid, c in self.comments.items()
                if self.root(cid) == cid and c.get("commit_title") in gone
            }
            approvals = {
                t
                for t in [*self.approvals, *(t for t, _ in self.file_verdicts)]
                if t in gone
            }
            if not roots and not approvals:
                return 0, 0
            kept = []
            for line in self.path.read_text().splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    kept.append(line)  # not ours to judge
                    continue
                if not isinstance(rec, dict):
                    kept.append(line)
                elif rec.get("type") == "approval":
                    if rec.get("commit_title") not in approvals:
                        kept.append(line)
                elif self.root(str(rec.get("id"))) not in roots:
                    kept.append(line)
            tmp = self.path.with_name(self.path.name + ".prune")
            tmp.write_text("".join(line + "\n" for line in kept))
            now = self.path.stat()
            if (now.st_size, now.st_mtime_ns) == (
                seen.st_size,
                seen.st_mtime_ns,
            ):
                os.replace(tmp, self.path)
                self.load()
                return len(roots), len(approvals)
            tmp.unlink(missing_ok=True)
        self.load()
        return 0, 0


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


def rec_key(rec: dict) -> str | None:
    """The unit a record is about, as Commit.key names it."""
    if unit := rec.get("unit"):
        return f"unit:{unit}"
    return rec.get("commit_title")


def key_fields(key: str) -> dict:
    """The fields that name a unit in a record."""
    if key.startswith("unit:"):
        return {"unit": key.removeprefix("unit:")}
    return {"commit_title": key}


def commits_titled(commits: list[Commit], key: object) -> list[int]:
    return [ci for ci, c in enumerate(commits) if c.key == key]


def place(
    c: dict,
    files: list[FileDiff],
    commits: list[Commit],
    branch: str | None = None,
) -> tuple:
    """Where a thread's root sits in this diff of a branch now.

    ("line", fi, hi, li), ("file", fi), ("commit", ci), ("outdated", ci), or
    ("elsewhere",) when it is about another branch, or no commit in the
    range has its title.
    """
    if branch and c.get("branch") and c["branch"] != branch:
        return ("elsewhere",)
    cis = commits_titled(commits, rec_key(c))
    if not cis:
        return ("elsewhere",)
    path = c.get("path")
    if not path:
        return ("commit", cis[0])
    if c.get("line_text") is None:
        for fi, f in enumerate(files):
            if f.commit in cis and path in (f.old_path, f.new_path):
                return ("file", fi)
        return ("outdated", cis[0])
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
