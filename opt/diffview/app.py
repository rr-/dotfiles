"""The diff viewer: its state, cursor and keys."""

import os
import re
import shlex
import subprocess
from pathlib import Path

from .draw import Draw
from .gitio import git_root, initial_context, run_git
from .highlight import Highlight, highlight_file
from .model import TRAILER_RE, Commit, FileDiff, Hunk, parse_diff, wrap
from .notes import NOTE_PROMPTS, Notes
from .review import Review
from .rows import Quit, Row
from .term import Mouse, Terminal
from .theme import PLAIN, Style, role
from .tree import Node, build_tree, walk_tree

CONTEXT_STEP = 3
FULL_CONTEXT = 1_000_000  # as -U, enough to show every line of a file


class App(Draw, Notes):
    def __init__(
        self,
        git_args: list[str] | None,
        text: str,
        review: Review | None = None,
        git_cmd: str = "diff",
    ) -> None:
        self.git_args = git_args
        self.git_cmd = git_cmd
        self.review = review
        self.hide_resolved = False
        self.prompt_target: tuple | None = None
        self.last_click, self.last_time = -1, 0.0
        self.tree_free = False  # the wheel scrolled the tree off its cursor
        self.help_top = 0
        self.root = git_root()
        self.folded: set[str] = set()
        self.cur = self.top = self.hscroll = 0
        self.focus = "diff"
        self.show_tree = True
        self.tree_cur = 0
        self.tree_top = 0
        self.count = ""
        self.pending = ""
        self.prompt: tuple[str, str] | None = None
        self.search: tuple[re.Pattern, int] | None = None
        self.message = ("", PLAIN)
        self.show_help = False
        self.width, self.height = 80, 24
        self.wrap_width = 0
        self.base_context = self.context = initial_context(git_args)
        self.full = False
        # Each file's hunks per -U, when they come from re-diffing blobs.
        self.hunk_cache: dict[
            tuple[int, int], tuple[list[Hunk], int, int]
        ] = {}
        self.load(text)

    # model

    def load(self, text: str) -> None:
        files, self.commits = parse_diff(text)
        tree = build_tree(files, self.commits)
        order = [
            n.file
            for _, n in walk_tree(tree, everything=True)
            if n.file is not None
        ]
        self.files = [files[i] for i in order]
        self.tree = build_tree(self.files, self.commits)
        self.highlights: dict[int, Highlight] = {}
        self.build_rows()

    def build_rows(self) -> None:
        # The diff pane shows one page at a time: a commit's message, or one
        # file. C-j and C-k walk the pages in tree order.
        self.rows: list[Row] = []
        self.pages: list[tuple[str, int]] = []
        self.spans: list[tuple[int, int]] = []
        self.file_rows: list[int] = []
        self.file_page: dict[int, int] = {}
        self.commit_page: dict[int, int] = {}
        shown = -1

        width = max(
            (
                len(str(n))
                for f in self.files
                for h in f.hunks
                for line in h.lines
                for n in (line.old, line.new)
                if n is not None
            ),
            default=1,
        )
        self.num_width = max(width, 3)
        self.place_threads()

        def add_page(kind: str, index: int, rows: list[Row]) -> int:
            page = len(self.pages)
            self.pages.append((kind, index))
            self.spans.append((len(self.rows), len(self.rows) + len(rows) - 1))
            for row in rows:
                row.page = page
            self.rows += rows
            return page

        def add_commits(upto: int) -> None:
            nonlocal shown
            for ci in range(shown + 1, upto + 1):
                rows = self.message_rows(ci)
                self.commit_page[ci] = add_page("commit", ci, rows)
            shown = max(shown, upto)

        for fi, f in enumerate(self.files):
            add_commits(f.commit)
            self.file_rows.append(len(self.rows))
            rows = [Row("file", fi)]
            if f.path not in self.folded:
                rows += [Row("meta", fi, text=m) for m in f.meta]
                for hi, hunk in enumerate(f.hunks):
                    if hunk.header:
                        rows.append(Row("hunk", fi, hi))
                    for li in range(len(hunk.lines)):
                        rows.append(Row("line", fi, hi, li))
                        rows += self.line_notes(fi, hi, li)
            self.file_page[fi] = add_page("file", fi, rows)
        add_commits(len(self.commits) - 1)

    def message_rows(self, ci: int) -> list[Row]:
        commit = self.commits[ci]
        width = self.wrap_width - 4 if self.wrap_width > 24 else 10**6
        texts: list[tuple[str, str]] = []
        if not commit.sha:  # some --format we don't know: show it as is
            texts = [("subject", commit.lines[0])]
            texts += [("", line) for line in commit.lines[1:]]
        else:
            head = " ".join([commit.sha, commit.author, commit.date])
            texts.append(("head", head))
            texts += [("dim", line) for line in commit.headers]
            texts.append(("", ""))
            last_para = len(commit.message)
            while last_para and commit.message[last_para - 1].strip():
                last_para -= 1
            trailers = all(
                TRAILER_RE.match(line) for line in commit.message[last_para:]
            )
            for i, line in enumerate(commit.message):
                tone = "subject" if i == 0 else ""
                if trailers and i >= last_para and last_para:
                    tone = "dim"
                texts += [(tone, part) for part in wrap(line, width)]
            if commit.extra:
                texts.append(("", ""))
                texts += [("dim", line) for line in commit.extra]
        rows = [
            Row("commit", -1, ci, li, text, tone)
            for li, (tone, text) in enumerate(texts)
        ]
        return rows + self.commit_notes(ci, len(rows))

    def rewrap(self, width: int) -> None:
        """Rebuild the message pages for a new pane width."""
        if width == self.wrap_width or not self.commits:
            self.wrap_width = width
            return
        page = self.current_page()
        lo = self.spans[page][0]
        cur, top = self.cur - lo, self.top - lo
        self.wrap_width = width
        self.build_rows()
        lo, hi = self.spans[page]
        self.cur = min(lo + cur, hi)
        self.top = min(lo + top, hi)

    def reload(self) -> None:
        self.reload_review()
        if self.git_args is None:
            self.flash(
                "can't rerun a diff that came from stdin", "state.error"
            )
            return
        mark = self.mark()
        self.load(run_git(self.git_cmd, self.diff_args()))
        if not self.files:
            raise Quit("no changes left")
        self.restore(mark)
        self.flash("reloaded")

    def mark(self) -> tuple:
        """Where the cursor is, in terms that survive rebuilding the rows."""
        row = self.rows[self.cur]
        offset = self.cur - self.spans[row.page][0]
        if row.file < 0:
            return row.page, offset, None, None, row.note
        f = self.files[row.file]
        line = None
        if row.kind in ("line", "note"):
            at = f.hunks[row.hunk].lines[row.line]
            line = (at.old, at.new)
        return row.page, offset, f.path, line, row.note

    def restore(self, mark: tuple) -> None:
        page, offset, path, line, note = mark
        page = self.clamp(page, 0, len(self.pages) - 1)
        kind, index = self.pages[page]
        if path is not None and (
            kind != "file" or self.files[index].path != path
        ):
            for fi, f in enumerate(self.files):
                if f.path == path:
                    page = self.file_page[fi]
                    break
        lo, hi = self.spans[page]
        self.cur = min(lo + offset, hi)
        if line is not None:
            old, new = line
            for i in range(lo, hi + 1):
                row = self.rows[i]
                if row.kind != "line":
                    continue
                at = self.files[row.file].hunks[row.hunk].lines[row.line]
                if new is not None:
                    found = at.new is not None and at.new >= new
                else:
                    found = at.old is not None and at.old >= old
                if found:
                    self.cur = i
                    break
        if note:
            self.cur = next(
                (i for i, row in enumerate(self.rows) if row.note == note),
                self.cur,
            )
        self.set_cur(self.cur, "center")

    # context

    @property
    def unified(self) -> int:
        return FULL_CONTEXT if self.full else self.context

    def diff_args(self) -> list[str]:
        args = list(self.git_args)
        if self.unified != self.base_context:
            # Before any `--`, where it would read as a path.
            at = args.index("--") if "--" in args else len(args)
            args.insert(at, f"-U{self.unified}")
        return args

    def set_context(self, context: int, full: bool) -> None:
        context = max(0, context)
        if (context, full) == (self.context, self.full):
            return
        mark = self.mark()
        self.context, self.full = context, full
        failed = 0
        if self.git_args is not None:
            self.load(run_git(self.git_cmd, self.diff_args()))
            if not self.files:
                raise Quit("no changes left")
        else:
            # From stdin there is no command to rerun, so each file is diffed
            # again from the blobs named on its index line.
            for fi, f in enumerate(self.files):
                if not self.recontext(fi, f):
                    failed += 1
            self.highlights = {}
            self.build_rows()
        self.restore(mark)
        what = "full file" if self.full else f"context {self.context}"
        if failed:
            noun = "file" if failed == 1 else "files"
            self.flash(
                f"{what}, but {failed} {noun} kept theirs: blobs not found",
                "state.warning",
            )
        else:
            self.flash(what)

    def recontext(self, fi: int, f: FileDiff) -> bool:
        if f.blobs is None or f.binary or f.status in "AD" or not f.hunks:
            return True  # nothing more to show
        cache = self.hunk_cache
        original = (f.hunks, f.added, f.deleted)
        cache.setdefault((fi, self.base_context), original)
        if (fi, self.unified) not in cache:
            proc = subprocess.run(
                [
                    "git",
                    "diff",
                    "--no-color",
                    "--no-ext-diff",
                    f"-U{self.unified}",
                    *f.blobs,
                ],
                capture_output=True,
            )
            if proc.returncode not in (0, 1):
                return False
            files, _ = parse_diff(proc.stdout.decode(errors="replace"))
            if not files:
                return False
            new = files[0]
            cache[fi, self.unified] = (new.hunks, new.added, new.deleted)
        f.hunks, f.added, f.deleted = cache[fi, self.unified]
        return True

    def highlight(self, fi: int) -> Highlight:
        if fi not in self.highlights:
            self.highlights[fi] = highlight_file(self.files[fi], self.root)
        return self.highlights[fi]

    def anchor(self, row: Row) -> int:
        if row.file < 0:
            return 1
        f = self.files[row.file]
        if row.kind in ("hunk", "line", "note") and f.hunks:
            hunk = f.hunks[row.hunk]
            return (
                hunk.new_start
                if row.kind == "hunk"
                else hunk.lines[row.line].anchor
            )
        return 1

    # geometry

    @property
    def body_h(self) -> int:
        return max(2, self.height - 1)

    @property
    def view_h(self) -> int:
        """Rows for the page, less the commit line pinned above a file."""
        return self.body_h - (1 if self.pinned_commit() is not None else 0)

    def pinned_commit(self) -> Commit | None:
        fi = self.current_file()
        if fi is None or self.files[fi].commit < 0:
            return None
        commit = self.commits[self.files[fi].commit]
        return commit if commit.sha else None

    @property
    def tree_visible(self) -> bool:
        return self.show_tree and self.width >= 50

    def tree_width(self) -> int:
        def room(depth: int, node: Node) -> int:
            n = depth * 2 + 2 + len(node.name) + (1 if node.is_dir else 0)
            if node.commit and node.rank >= 0 and self.review is not None:
                # a badge, and the start of the subject
                n += 4 + min(30, len(self.commits[node.rank].subject))
            return n

        widest = max(
            (
                room(depth, node)
                for depth, node in walk_tree(self.tree, everything=True)
            ),
            default=10,
        )
        return max(16, min(widest + 2, self.width // 3))

    # cursor

    def clamp(self, n: int, lo: int, hi: int) -> int:
        return max(lo, min(n, hi))

    @property
    def span(self) -> tuple[int, int]:
        return self.spans[self.current_page()]

    def move(self, row: int, align: str | None = None) -> None:
        """Move the cursor without leaving the current page."""
        self.set_cur(self.clamp(row, *self.span), align)

    def set_cur(self, row: int, align: str | None = None) -> None:
        self.cur = self.clamp(row, 0, len(self.rows) - 1)
        h = self.view_h
        if align == "top":
            self.top = self.cur
        elif align == "center" or (
            align == "jump" and not self.top <= self.cur < self.top + h
        ):
            self.top = self.cur - h // 2
        self.follow()

    def follow(self) -> None:
        h = self.view_h
        if self.cur < self.top:
            self.top = self.cur
        if self.cur >= self.top + h:
            self.top = self.cur - h + 1
        lo, hi = self.span
        self.top = self.clamp(self.top, lo, max(lo, hi - h + 1))

    def scroll(self, delta: int, move_cursor: bool) -> None:
        h = self.view_h
        lo, hi = self.span
        self.top = self.clamp(self.top + delta, lo, max(lo, hi - h + 1))
        if move_cursor:
            self.cur = self.clamp(self.cur + delta, lo, hi)
        self.cur = self.clamp(self.cur, self.top, min(self.top + h - 1, hi))

    def current_page(self) -> int:
        return self.rows[self.cur].page

    def current_file(self) -> int | None:
        fi = self.rows[self.cur].file
        return fi if fi >= 0 else None

    def goto_page(self, page: int) -> None:
        page = self.clamp(page, 0, len(self.pages) - 1)
        self.set_cur(self.spans[page][0], "top")

    def goto_file(self, fi: int) -> None:
        self.goto_page(self.file_page[fi])

    def goto_next(self, kind: str, step: int) -> None:
        """Jump to the next hunk or commit header."""
        rng = (
            range(self.cur + 1, len(self.rows))
            if step > 0
            else range(self.cur - 1, -1, -1)
        )
        for i in rng:
            row = self.rows[i]
            if row.kind == kind and (kind != "commit" or row.line == 0):
                self.set_cur(i, "top" if kind == "commit" else "jump")
                return
        self.flash(f"no more {kind}s", "state.warning")

    def goto_line(self, n: int) -> None:
        fi = self.current_file()
        if fi is None:
            self.flash("not on a file", "state.error")
            return
        lo, hi = self.span
        best = lo
        for i in range(lo, hi + 1):
            row = self.rows[i]
            if row.kind != "line":
                continue
            line = self.files[fi].hunks[row.hunk].lines[row.line]
            if line.new is not None and line.new <= n:
                best = i
            if line.new is not None and line.new >= n:
                break
        self.set_cur(best, "jump")

    def toggle_fold(
        self, paths: set[str] | None = None, fold: bool | None = None
    ) -> None:
        fi = self.current_file()
        page = self.current_page()
        if paths is None:
            if fi is None:
                self.flash("only files fold", "state.error")
                return
            self.folded ^= {self.files[fi].path}
        elif fold:
            self.folded |= paths
        else:
            self.folded -= paths
        self.build_rows()
        self.set_cur(self.spans[page][0])

    # tree

    def tree_rows(self) -> list[tuple[int, Node]]:
        return list(walk_tree(self.tree))

    def node_page(self, node: Node) -> int | None:
        if node.file is not None:
            return self.file_page[node.file]
        if node.message is not None:
            return self.commit_page[node.message]
        return None

    def sync_tree(self) -> None:
        self.tree_free = False
        page = self.current_page()
        node = next(
            n
            for _, n in walk_tree(self.tree, everything=True)
            if self.node_page(n) == page
        )
        parent = node.parent
        while parent is not None:
            parent.expanded = True
            parent = parent.parent
        self.tree_cur = [n for _, n in self.tree_rows()].index(node)

    def tree_move(self, index: int) -> None:
        rows = self.tree_rows()
        self.tree_cur = self.clamp(index, 0, len(rows) - 1)
        page = self.node_page(rows[self.tree_cur][1])
        if page is not None and page != self.current_page():
            self.goto_page(page)

    def tree_key(self, key: str, n: int | None) -> None:
        self.tree_free = False
        rows = self.tree_rows()
        node = rows[self.tree_cur][1]
        if key in ("j", "down", "C-n"):
            self.tree_move(self.tree_cur + (n or 1))
        elif key in ("k", "up", "C-p"):
            self.tree_move(self.tree_cur - (n or 1))
        elif key == "gg":
            self.tree_move(0)
        elif key == "G":
            self.tree_move(len(rows) - 1)
        elif key in ("enter", "o", "l", "right", " "):
            if node.is_dir:
                node.expanded = not node.expanded if key != "l" else True
            else:
                self.goto_page(self.node_page(node))
                if key in ("enter", "o", "l", "right"):
                    self.focus = "diff"
        elif key in ("h", "left"):
            if node.is_dir and node.expanded:
                node.expanded = False
            elif node.parent is not self.tree:
                self.tree_cur = [n for _, n in rows].index(node.parent)
        else:
            return
        self.pending = ""

    # input

    def flash(self, text: str, color: str | None = None) -> None:
        self.message = (text, Style(fg=role(color) if color else None))

    def handle(self, key: str) -> None:
        if self.show_help:
            self.help_key(key)
            return
        if self.prompt is not None:
            self.prompt_key(key)
            return
        self.message = ("", PLAIN)

        if key.isdigit() and (self.count or key != "0") and not self.pending:
            self.count += key
            return
        n = int(self.count) if self.count else None
        self.count = ""

        if self.pending == "C-w":
            self.pending = ""
            if key in ("h", "C-h", "left"):
                self.focus = "tree" if self.tree_visible else "diff"
            elif key in ("l", "C-l", "right"):
                self.focus = "diff"
            elif key in ("w", "C-w"):
                self.toggle_focus()
            return
        if self.pending:
            key, self.pending = self.pending + key, ""
        elif key in ("g", "z", "Z", "[", "]", "C-w"):
            self.pending = key
            return

        if self.focus == "tree" and self.tree_visible:
            self.tree_key(key, n)
            if key in (
                "j",
                "k",
                "down",
                "up",
                "C-n",
                "C-p",
                "gg",
                "G",
                "enter",
                "o",
                "l",
                "h",
                "left",
                "right",
                " ",
            ):
                return
        self.common_key(key, n)
        self.sync_tree()

    def toggle_focus(self) -> None:
        if self.focus == "diff" and self.tree_visible:
            self.focus = "tree"
            self.sync_tree()
        else:
            self.focus = "diff"

    def common_key(self, key: str, n: int | None) -> None:
        h = self.view_h
        lo, hi = self.span
        match key:
            case "q" | "ZZ" | "ZQ" | "C-c":
                raise Quit()
            case "j" | "down" | "C-n" | "enter":
                self.move(self.cur + (n or 1))
            case "k" | "up" | "C-p":
                self.move(self.cur - (n or 1))
            case "C-d":
                self.scroll(n or h // 2, True)
            case "C-u":
                self.scroll(-(n or h // 2), True)
            case "C-f" | "pgdn" | " ":
                self.scroll(max(1, h - 2) * (n or 1), True)
            case "C-b" | "pgup":
                self.scroll(-max(1, h - 2) * (n or 1), True)
            case "C-e":
                self.scroll(n or 1, False)
            case "C-y":
                self.scroll(-(n or 1), False)
            case "gg" | "home":
                self.move(lo + (n or 1) - 1, "jump")
            case "G" | "end":
                self.move(lo + n - 1 if n else hi, "jump")
            case "H":
                self.move(self.top + (n or 1) - 1)
            case "M":
                self.move(self.top + (min(h, hi - self.top + 1) - 1) // 2)
            case "L":
                self.move(min(self.top + h - 1, hi) - (n or 1) + 1)
            case "zz":
                self.set_cur(self.cur, "center")
            case "zt":
                self.set_cur(self.cur, "top")
            case "zb":
                self.top = self.cur - h + 1
                self.follow()
            case "h" | "left" | "zh":
                self.hscroll = max(0, self.hscroll - (n or 8))
            case "l" | "right" | "zl":
                self.hscroll += n or 8
            case "0":
                self.hscroll = 0
            case "$":
                self.hscroll = max(
                    0, self.widest_line() - self.diff_width() + 12
                )
            case "C-j" | "J" | "]f":
                self.goto_page(self.current_page() + (n or 1))
            case "C-k" | "K" | "[f":
                self.goto_page(self.current_page() - (n or 1))
            case "}" | "]c":
                for _ in range(n or 1):
                    self.goto_next("hunk", 1)
            case "{" | "[c":
                for _ in range(n or 1):
                    self.goto_next("hunk", -1)
            case "]]":
                for _ in range(n or 1):
                    self.goto_next("commit", 1)
            case "[[":
                for _ in range(n or 1):
                    self.goto_next("commit", -1)
            case "za":
                self.toggle_fold()
            case "zM":
                self.toggle_fold({f.path for f in self.files}, True)
            case "zR":
                self.toggle_fold(set(self.folded), False)
            case "tab":
                self.toggle_focus()
            case "t":
                self.show_tree = not self.show_tree
                self.focus = "diff"
            case "/" | "?" | ":":
                self.prompt = (key, "")
            case "n":
                self.search_next(1)
            case "N":
                self.search_next(-1)
            case "e":
                self.edit()
            case "r":
                self.reload()
            case "+":
                self.set_context(self.context + (n or CONTEXT_STEP), False)
            case "-":
                self.set_context(self.context - (n or CONTEXT_STEP), False)
            case "=":
                self.set_context(self.base_context, False)
            case "F":
                self.set_context(self.context, not self.full)
            case "c":
                self.start_comment()
            case "C":
                self.start_comment(whole_commit=True)
            case "x":
                self.toggle_resolve()
            case "a":
                self.toggle_approve()
            case "]n":
                for _ in range(n or 1):
                    self.goto_thread(1)
            case "[n":
                for _ in range(n or 1):
                    self.goto_thread(-1)
            case "zu":
                self.toggle_hide_resolved()
            case "C-l":
                pass
            case _:
                if key not in ("esc",):
                    self.flash(
                        f"{key} does nothing - :h for help", "text.faint"
                    )

    def prompt_key(self, key: str) -> None:
        kind, text = self.prompt
        if key in ("esc", "C-c") or (key == "backspace" and not text):
            self.prompt = None
            if kind in NOTE_PROMPTS:
                self.prompt_target = None
                self.flash("dropped the comment" if text else "")
        elif key == "C-e" and kind in NOTE_PROMPTS:
            self.prompt = None
            self.submit_comment(self.edit_text(text) or "")
        elif key == "backspace":
            self.prompt = (kind, text[:-1])
        elif key == "C-u":
            self.prompt = (kind, "")
        elif key == "C-w":
            self.prompt = (kind, re.sub(r"\S*\s*$", "", text))
        elif key == "enter":
            self.prompt = None
            if kind in NOTE_PROMPTS:
                self.submit_comment(text)
            elif kind == ":":
                self.command(text.strip())
            elif text or self.search:
                self.start_search(text, 1 if kind == "/" else -1)
        elif len(key) == 1:
            self.prompt = (kind, text + key)

    def command(self, cmd: str) -> None:
        if cmd.isdigit():
            self.goto_line(int(cmd))
        elif cmd in ("q", "q!", "qa", "qa!", "quit", "x"):
            raise Quit()
        elif cmd in ("h", "help"):
            self.show_help = True
            self.help_top = 0
        elif cmd:
            self.flash(f"not a command: {cmd}", "state.error")

    def start_search(self, pattern: str, direction: int) -> None:
        if pattern:
            try:
                flags = re.I if pattern == pattern.lower() else 0
                self.search = (re.compile(pattern, flags), direction)
            except re.error as ex:
                self.flash(f"bad pattern: {ex}", "state.error")
                return
        else:
            self.search = (self.search[0], direction)
        self.search_next(1)

    def row_text(self, row: Row) -> str:
        if row.kind in ("commit", "note"):
            return row.text
        f = self.files[row.file]
        match row.kind:
            case "file":
                return f.label
            case "hunk":
                return f.hunks[row.hunk].header
            case "line":
                return f.hunks[row.hunk].lines[row.line].text
            case "meta":
                return row.text
        return ""

    def search_next(self, step: int) -> None:
        if not self.search:
            self.flash("no previous search", "state.error")
            return
        pattern, direction = self.search
        step *= direction
        count = len(self.rows)
        for off in range(1, count + 1):
            i = (self.cur + off * step) % count
            if pattern.search(self.row_text(self.rows[i])):
                wrapped = (i < self.cur) if step > 0 else (i > self.cur)
                self.set_cur(i, "jump")
                if wrapped:
                    self.flash("search wrapped around", "state.warning")
                return
        self.flash(f"pattern not found: {pattern.pattern}", "state.error")

    def edit(self) -> None:
        row = self.rows[self.cur]
        if row.file < 0:
            self.flash("not on a file", "state.error")
            return
        f = self.files[row.file]
        if f.new_path is None:
            self.flash("that file is gone", "state.error")
            return
        candidates = [Path(f.new_path)]
        if self.root is not None:
            candidates.insert(0, self.root / f.new_path)
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            self.flash(f"can't find {f.new_path}", "state.error")
            return
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
        self.term.suspend()
        try:
            subprocess.run(
                [*shlex.split(editor), f"+{self.anchor(row)}", str(path)],
                stdin=self.term.fd,
                stdout=self.term.fd,
                stderr=self.term.fd,
            )
        finally:
            self.term.resume()
        if self.git_args is not None:
            self.reload()

    def run(self) -> None:
        with Terminal() as self.term:
            self.flash(":help for the keys", "text.faint")
            while True:
                self.draw()
                key = self.term.read_key()
                if key is None:
                    continue
                try:
                    if isinstance(key, Mouse):
                        self.mouse(key)
                    else:
                        self.handle(key)
                except Quit:
                    return
