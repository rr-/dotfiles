"""A review of some units of code, apart from any way of showing it.

A unit is what a review judges as one: today a commit, whose title is its
key in the review file. The units come as the diff model has them, files
and the commits they belong to; the session places every thread on them,
counts what is open, and is the one place that writes comments, replies,
resolutions and verdicts. The viewer and git review list both read it.

A target is what a new comment is about:

    ("line", fi, hi, li)   one line of a file's diff
    ("file", fi)           a whole file
    ("commit", ci)         a whole unit
"""

from .model import Commit, FileDiff
from .review import Review, key_fields, make_anchor, place

VERDICTS = ("approved", "changes requested")


class Session:
    def __init__(
        self, store: Review, files: list[FileDiff], commits: list[Commit]
    ) -> None:
        self.store = store
        self.files = files
        self.commits = commits
        self.place()

    # units

    def unit_key(self, ci: int) -> str:
        return self.commits[ci].key

    def unit_of(self, target: tuple) -> int:
        if target[0] == "commit":
            return target[1]
        return self.files[target[1]].commit

    def has_key(self, ci: int) -> bool:
        return ci >= 0 and bool(self.unit_key(ci))

    # placing

    def place(self) -> None:
        """Find every thread's spot, and count them per unit and file."""
        self.placed: dict[str, tuple] = {}
        self.at_line: dict[tuple[int, int, int], list[dict]] = {}
        self.at_file: dict[int, list[dict]] = {}
        self.at_commit: dict[int, list[dict]] = {}
        self.open_threads: dict[int, int] = {}
        # per file: its open threads, and all of them
        self.file_threads: dict[int, tuple[int, int]] = {}
        store = self.store
        for root in store.threads():
            where = place(root, self.files, self.commits, store.branch)
            self.placed[root["id"]] = where
            if where[0] == "line":
                self.at_line.setdefault(where[1:], []).append(root)
            elif where[0] == "file":
                self.at_file.setdefault(where[1], []).append(root)
            elif where[0] in ("commit", "outdated"):
                self.at_commit.setdefault(where[1], []).append(root)
            else:
                continue
            is_open = store.is_open(root["id"])
            if where[0] in ("line", "file"):
                n_open, n_all = self.file_threads.get(where[1], (0, 0))
                self.file_threads[where[1]] = (n_open + is_open, n_all + 1)
            if is_open:
                ci = self.unit_at(where)
                self.open_threads[ci] = self.open_threads.get(ci, 0) + 1
        for roots in self.at_commit.values():
            # the whole unit's threads first, then those that lost a line
            roots.sort(key=lambda r: self.placed[r["id"]][0] == "outdated")

    def unit_at(self, where: tuple) -> int:
        if where[0] in ("line", "file"):
            return self.files[where[1]].commit
        return where[1]

    def threads_of(self, ci: int) -> list[dict]:
        """Every thread on a unit, in the order the review file has them."""
        return [
            root
            for root in self.store.threads()
            if self.placed.get(root["id"], ("elsewhere",))[0] != "elsewhere"
            and self.unit_at(self.placed[root["id"]]) == ci
        ]

    def elsewhere(self) -> int:
        """Open threads on no unit here: another branch, or a title gone."""
        return sum(
            self.store.is_open(rid)
            for rid, where in self.placed.items()
            if where[0] == "elsewhere"
        )

    # writing

    def comment(self, target: tuple, text: str, author: str = "me") -> str:
        ci = self.unit_of(target)
        fields: dict = key_fields(self.unit_key(ci))
        if target[0] == "line":
            _, fi, hi, li = target
            fields |= make_anchor(self.files[fi], hi, li)
        else:
            path = self.files[target[1]].path if target[0] == "file" else None
            fields |= {"path": path, "side": None, "line_text": None}
            fields["line"] = None
        cid = self.store.add(author, text, **fields)
        self.place()
        return cid

    def reply(self, rid: str, text: str, author: str = "me") -> bool:
        """Answer a thread, opening it again if it was resolved. Gives
        whether it was."""
        self.store.add(author, text, reply_to=rid)
        reopened = not self.store.is_open(rid)
        if reopened:
            self.store.update(rid, status="open")
        self.place()
        return reopened

    def toggle_resolve(self, rid: str) -> bool:
        """Resolve a thread, or open it again. Gives whether it is
        resolved now."""
        resolve = self.store.is_open(rid)
        self.store.update(rid, status="resolved" if resolve else "open")
        self.place()
        return resolve

    # verdicts

    def verdict(self, ci: int | None) -> str:
        if ci is None or not self.has_key(ci):
            return ""
        return self.store.verdict(self.unit_key(ci))

    def toggle_verdict(self, ci: int, verdict: str) -> str:
        """Give a unit a verdict, or take it back if it has it. Gives the
        verdict it has now."""
        assert verdict in VERDICTS
        now = "" if self.verdict(ci) == verdict else verdict
        self.store.approve(
            self.unit_key(ci),
            now == "approved",
            now == "changes requested",
        )
        return now

    def file_verdict(self, fi: int) -> str:
        ci = self.files[fi].commit
        if not self.has_key(ci):
            return ""
        return self.store.file_verdict(self.unit_key(ci), self.files[fi].path)

    def toggle_file_verdict(self, fi: int, verdict: str) -> str:
        """As toggle_verdict, for one file of a unit."""
        assert verdict in VERDICTS
        now = "" if self.file_verdict(fi) == verdict else verdict
        self.store.approve(
            self.unit_key(self.files[fi].commit),
            now == "approved",
            now == "changes requested",
            path=self.files[fi].path,
        )
        return now

    def file_verdicts_of(self, ci: int) -> list[tuple[str, str]]:
        """The files of a unit that have a verdict, with it."""
        return [
            (f.path, v)
            for fi, f in enumerate(self.files)
            if f.commit == ci and (v := self.file_verdict(fi))
        ]

    def summary(self) -> tuple[int, int, int]:
        """Open threads, approved units, and units."""
        keyed = [ci for ci in range(len(self.commits)) if self.has_key(ci)]
        approved = sum(self.verdict(ci) == "approved" for ci in keyed)
        return sum(self.open_threads.values()), approved, len(keyed)
