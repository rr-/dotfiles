"""Review comments in the viewer: their rows, keys and the mouse."""

import os
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

from .model import relative_date, wrap
from .review import Review, can_anchor, make_anchor
from .rows import Row
from .session import Session
from .term import LineBuf, Mouse
from .theme import VERDICT_CHIP, VERDICT_MARK, Style, role

NOTE_PROMPTS = {"comment": "comment: ", "reply": "reply: "}
DOUBLE_CLICK = 0.5
WHEEL_STEP = 3


class Notes:
    review: Review | None

    # placing

    def place_threads(self) -> None:
        """A session over the units now shown, and its counts as ours."""
        self.session = None
        if self.review is not None:
            self.session = Session(self.review, self.files, self.commits)
        s = self.session
        self.placed = s.placed if s else {}
        self.at_line = s.at_line if s else {}
        self.at_file = s.at_file if s else {}
        self.at_commit = s.at_commit if s else {}
        self.open_threads = s.open_threads if s else {}
        self.file_threads = s.file_threads if s else {}

    def line_notes(self, fi: int, hi: int, li: int) -> list[Row]:
        rows: list[Row] = []
        for root in self.at_line.get((fi, hi, li), []):
            rows += self.thread_rows(root, fi, hi, li)
        return rows

    def file_notes(self, fi: int) -> list[Row]:
        """Threads about a whole file, under its header. Their rows have
        no hunk: hunk -1."""
        rows: list[Row] = []
        for root in self.at_file.get(fi, []):
            rows += self.thread_rows(root, fi, -1, 0)
        return rows

    def commit_notes(self, ci: int, start: int) -> list[Row]:
        rows: list[Row] = []
        for root in self.at_commit.get(ci, []):
            thread = self.thread_rows(root, -1, ci, 0)
            if thread:
                rows.append(Row("commit", -1, ci, start + len(rows)))
                rows += thread
        return rows

    def note_indent(self, fi: int) -> int:
        return 2 if fi < 0 else self.num_width * 2 + 4

    def thread_rows(self, root: dict, fi: int, hi: int, li: int) -> list[Row]:
        rid = root["id"]
        if self.hide_resolved and not self.review.is_open(rid):
            return []
        room = (self.wrap_width or 10**6) - self.note_indent(fi) - 4
        width = max(20, room)
        rows: list[Row] = []

        def add(tone: str, text: str, cid: str) -> None:
            rows.append(
                Row("note", fi, hi, li, text, tone, note=cid, thread=rid)
            )

        for c in [root, *self.review.replies(rid)]:
            add("head", str(c.get("author", "?")), c["id"])
            if c is root and self.placed.get(rid, ("",))[0] == "outdated":
                where = str(root.get("path"))
                if root.get("line_text") is not None:
                    where += f":{root.get('line')}"
                text = str(root.get("line_text", "")).strip()
                add("where", f"was on {where}: {text}", rid)
            for para in str(c.get("text", "")).split("\n"):
                for part in wrap(para, width):
                    add("body", part, c["id"])
        return rows

    # where the cursor is

    def current_commit(self) -> int | None:
        kind, index = self.pages[self.current_page()]
        ci = index if kind == "commit" else self.files[index].commit
        if ci < 0 or not self.commits[ci].key:
            return None
        return ci

    def reviewing(self) -> bool:
        if self.review is None:
            self.flash("not a review - see git review --help", "state.error")
        return self.review is not None

    # keys

    def start_comment(self, whole_commit: bool = False) -> None:
        if not self.reviewing():
            return
        row = self.rows[self.cur]
        if row.kind == "note" and not whole_commit:
            author = self.review.comments[row.thread].get("author", "?")
            self.prompt_target = ("reply", row.thread)
            self.open_prompt("reply")
            if not self.message[0]:
                self.flash(f"replying to {author}")
            return
        if row.kind == "line" and not whole_commit:
            f = self.files[row.file]
            if not can_anchor(f.hunks[row.hunk].lines[row.line]):
                self.flash("can't comment on that line", "state.error")
                return
            if f.commit < 0 or not self.commits[f.commit].key:
                self.flash("that line is in no commit", "state.error")
                return
            self.prompt_target = ("line", row.file, row.hunk, row.line)
        elif row.kind in ("file", "meta", "hunk") and not whole_commit:
            f = self.files[row.file]
            if f.commit < 0 or not self.commits[f.commit].key:
                self.flash("that file is in no commit", "state.error")
                return
            self.prompt_target = ("file", row.file)
            self.flash(f"on the whole file: {f.path}")
        else:
            ci = self.current_commit()
            if ci is None:
                self.flash("not in a commit", "state.error")
                return
            self.prompt_target = ("commit", ci)
            self.flash(
                f"on the whole of {self.commits[ci].subject or self.commits[ci].lines[0]}"
            )
        self.open_prompt("comment")

    def draft_key(self, target: tuple) -> tuple:
        """The target in terms that survive reloading the diff."""
        if target[0] == "line":
            _, fi, hi, li = target
            f = self.files[fi]
            anchor = make_anchor(f, hi, li)
            return (
                self.commits[f.commit].key,
                anchor["path"],
                anchor["side"],
                anchor["line_text"],
                anchor["line"],
            )
        if target[0] == "commit":
            return ("commit", self.commits[target[1]].key)
        if target[0] == "file":
            f = self.files[target[1]]
            return ("file", self.commits[f.commit].key, f.path)
        return target

    def open_prompt(self, kind: str) -> None:
        text = self.drafts.pop(self.draft_key(self.prompt_target), "")
        self.prompt = (kind, text)
        self.prompt_pos = len(text)
        if text:
            self.flash("your draft is back")

    def keep_draft(self, text: str) -> None:
        target, self.prompt_target = self.prompt_target, None
        if text.strip() and target is not None:
            self.drafts[self.draft_key(target)] = text
            self.flash("kept as a draft: c here brings it back")

    def submit_comment(self, text: str) -> None:
        text = text.strip()
        target, self.prompt_target = self.prompt_target, None
        if target is not None:
            self.drafts.pop(self.draft_key(target), None)
        if not text or target is None:
            self.flash("nothing to save", "text.faint")
            return
        mark = self.mark()
        if target[0] == "reply":
            if self.session.reply(target[1], text):
                self.flash("replied, and opened the thread again")
            else:
                self.flash("replied")
        else:
            self.session.comment(target, text)
            self.flash(
                {
                    "line": "commented",
                    "file": "commented on the file",
                    "commit": "commented on the commit",
                }[target[0]]
            )
        self.build_rows()
        self.restore(mark)

    def edit_text(self, text: str) -> str | None:
        """Text written in $EDITOR, or None when it comes back empty."""
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", prefix="review-", delete=False
        ) as handle:
            handle.write(text)
        path = Path(handle.name)
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
        self.term.suspend()
        try:
            subprocess.run(
                [*shlex.split(editor), str(path)],
                stdin=self.term.fd,
                stdout=self.term.fd,
                stderr=self.term.fd,
            )
            return path.read_text().strip() or None
        finally:
            self.term.resume()
            path.unlink(missing_ok=True)

    def toggle_resolve(self) -> None:
        if not self.reviewing():
            return
        row = self.rows[self.cur]
        if row.kind != "note":
            self.flash("not on a comment", "state.error")
            return
        mark = self.mark()
        resolved = self.session.toggle_resolve(row.thread)
        self.build_rows()
        self.restore(mark)
        self.flash("resolved" if resolved else "opened again")

    def toggle_approve(self) -> None:
        self.toggle_here("approved")

    def toggle_changes(self) -> None:
        self.toggle_here("changes requested")

    def toggle_here(self, verdict: str) -> None:
        """Give a verdict to the file whose page this is, or on a commit's
        message page to the commit, or take it back."""
        if not self.reviewing():
            return
        ci = self.current_commit()
        if ci is None:
            self.flash("not in a commit", "state.error")
            return
        kind, index = self.pages[self.current_page()]
        if kind == "file":
            what = self.files[index].path
            now = self.session.toggle_file_verdict(index, verdict)
        else:
            what = self.commits[ci].subject or self.commits[ci].lines[0]
            now = self.session.toggle_verdict(ci, verdict)
        if not now:
            self.flash(f"took back the verdict on {what}")
        elif now == "changes requested":
            self.flash(f"changes requested on {what}", "state.error")
        elif kind == "commit" and (n := self.open_threads.get(ci)):
            noun = "thread" if n == 1 else "threads"
            self.flash(f"approved, with {n} open {noun}", "state.warning")
        else:
            self.flash(f"approved {what}", "state.success")

    def toggle_hide_resolved(self) -> None:
        if not self.reviewing():
            return
        self.hide_resolved = not self.hide_resolved
        mark = self.mark()
        self.build_rows()
        self.restore(mark)
        self.flash(
            "resolved threads hidden"
            if self.hide_resolved
            else "resolved threads shown"
        )

    def goto_thread(self, step: int) -> None:
        if not self.reviewing():
            return
        heads = [
            i
            for i, row in enumerate(self.rows)
            if row.kind == "note"
            and row.tone == "head"
            and row.note == row.thread
            and self.review.is_open(row.thread)
        ]
        if not heads:
            self.flash("no open threads", "state.warning")
            return
        if step > 0:
            later = [i for i in heads if i > self.cur]
            target = later[0] if later else heads[0]
        else:
            earlier = [i for i in heads if i < self.cur]
            target = earlier[-1] if earlier else heads[-1]
        if (target > self.cur) != (step > 0):
            self.flash("search wrapped around", "state.warning")
        self.set_cur(target, "center")

    def reload_review(self) -> None:
        if self.review is not None:
            self.review.load()
            if self.review.bad:
                noun = "line" if self.review.bad == 1 else "lines"
                self.flash(
                    f"skipped {self.review.bad} bad {noun} of "
                    f"{self.review.path}",
                    "state.warning",
                )

    # the summary

    def verdict(self, ci: int | None) -> str:
        return self.session.verdict(ci) if self.session else ""

    def file_verdict(self, fi: int) -> str:
        return self.session.file_verdict(fi) if self.session else ""

    def here_verdict(self) -> str:
        """The verdict M-a and M-r would change: the open file's, or on a
        message page the commit's."""
        kind, index = self.pages[self.current_page()]
        if kind == "file":
            return self.file_verdict(index)
        return self.verdict(self.current_commit())

    def approved(self, ci: int) -> bool:
        return self.verdict(ci) == "approved"

    def add_verdict(self, buf: LineBuf, verdict: str) -> None:
        """A chip no one can miss on a commit with a verdict."""
        mark = VERDICT_MARK[verdict]
        buf.add(f" {mark} {verdict.upper()} ", VERDICT_CHIP[verdict])

    def file_badge(self, fi: int) -> tuple[str, str]:
        """●N for a file's open threads, ○ when all are resolved."""
        n_open, n_all = self.file_threads.get(fi, (0, 0))
        if n_open:
            return f" ●{n_open}", "state.warning"
        if n_all:
            return " ○", "text.faint"
        return "", ""

    def commit_badge(self, ci: int) -> tuple[str, str] | None:
        if self.review is None or ci < 0:
            return None
        approved = self.verdict(ci) == "approved"
        if n := self.open_threads.get(ci):
            return f"{'✓' if approved else ''}●{n}", "state.warning"
        if approved:
            return "✓", "state.success"
        return None

    def review_summary(self) -> str:
        if self.session is None:
            return ""
        open_, approved, units = self.session.summary()
        return f"{open_} open  ✓{approved}/{units}"

    # drawing

    def draw_note(
        self, buf: LineBuf, row: Row, is_cur: bool, sign_col
    ) -> None:
        c = self.review.comments.get(row.note, {})
        resolved = not self.review.is_open(row.thread)
        sign_col()
        buf.add(" " * self.note_indent(row.file), Style())
        bg = role("surface.overlay" if is_cur else "surface.raised")
        author = c.get("author", "?")
        bar = role("accent.link" if author == "claude" else "accent.primary")
        if resolved:
            bar = role("text.faint")
        base = Style(bg=bg, fg=role("text.muted") if resolved else None)
        faint = Style(fg=role("text.faint"), bg=bg)
        buf.add("▎ ", Style(fg=bar, bg=bg))
        if row.tone == "head":
            buf.add(author, base._replace(fg=bar, bold=True))
            buf.add(" · " + relative_date(str(c.get("created", ""))), faint)
            if row.note == row.thread:
                where = self.placed.get(row.thread, ("",))[0]
                tag, color = ("open", "state.warning")
                if resolved:
                    tag, color = ("resolved", "state.success")
                if where == "outdated":
                    tag += ", outdated"
                buf.add(" · ", faint)
                buf.add(tag, Style(fg=role(color), bg=bg, bold=True))
                buf.add(f"  #{row.thread}", faint)
        elif row.tone == "where":
            buf.add(row.text, faint)
        else:
            buf.add(row.text, base)
        buf.fill(Style(bg=bg))

    # mouse

    def mouse(self, ev: Mouse) -> None:
        if self.show_help or self.alert:
            if ev.button & 64:
                self.help_scroll(WHEEL_STEP if ev.button & 1 else -WHEEL_STEP)
            elif ev.press:
                self.show_help = False
                self.alert = None
            return
        if self.prompt is not None:
            return
        button = ev.button & ~(4 | 8 | 16)  # shift, alt and ctrl
        tree_w = self.tree_width() if self.tree_visible else 0
        in_tree = ev.x <= tree_w
        if button in (64, 65):
            step = WHEEL_STEP if button == 65 else -WHEEL_STEP
            if in_tree:
                self.tree_top = max(0, self.tree_top + step)
                self.tree_free = True
            else:
                self.scroll(step, False)
            return
        if button != 0 or not ev.press:
            return
        self.message = ("", Style())
        y = ev.y - 1
        if y >= self.body_h or ev.x == tree_w + 1 and tree_w:
            return
        if in_tree:
            self.click_tree(y)
            return
        self.focus = "diff"
        if self.pinned_commit() is not None:
            if y == 0:
                ci = self.files[self.current_file()].commit
                self.goto_page(self.commit_page[ci])
                self.sync_tree()
                return
            y -= 1
        i = self.top + y
        if i > self.span[1]:
            return
        now = time.monotonic()
        double = self.last_click == i and now - self.last_time < DOUBLE_CLICK
        self.last_click, self.last_time = i, now
        self.set_cur(i)
        self.sync_tree()
        if double and self.review is not None:
            self.last_click = -1
            self.start_comment()

    def click_tree(self, y: int) -> None:
        rows = self.tree_rows()
        i = self.tree_top + y - 1  # below the title
        if y == 0 or i >= len(rows):
            return
        self.focus = "tree"
        self.tree_free = False
        self.tree_cur = i
        node = rows[i][1]
        if node.is_dir:
            node.expanded = not node.expanded
        else:
            self.goto_page(self.node_page(node))
