"""Drawing the tree, the diff and the status line."""

from .help import HELP
from .model import Commit, relative_date
from .notes import NOTE_PROMPTS
from .rows import Row
from .term import TAB, LineBuf, cwidth, expand
from .theme import (
    NEON_CHIP,
    NEON_TEXT,
    PLAIN,
    Color,
    Style,
    role,
    sgr,
    token_color,
)
from .tree import tree_guides


class Draw:
    # drawing

    def diff_width(self) -> int:
        if self.tree_visible:
            return self.width - self.tree_width() - 1
        return self.width

    def widest_line(self) -> int:
        return max(
            (
                len(line.text.expandtabs(TAB))
                for f in self.files
                for h in f.hunks
                for line in h.lines
            ),
            default=0,
        )

    def draw(self) -> None:
        self.width, self.height = self.term.size()
        self.rewrap(self.diff_width())
        self.follow()
        if self.focus == "tree" and not self.tree_visible:
            self.focus = "diff"
        out = ["\x1b[?2026h"]
        tree_w = self.tree_width() if self.tree_visible else 0
        diff_w = self.diff_width()
        tree_lines = self.draw_tree(tree_w) if tree_w else []
        diff_lines = self.draw_diff(diff_w)
        sep = sgr(Style(fg=role("text.faint"))) + "│\x1b[0m"
        for y in range(self.body_h):
            out.append(f"\x1b[{y + 1};1H")
            if tree_w:
                out.append(tree_lines[y] + sep)
            out.append(diff_lines[y])
        if self.show_help:
            out.append(self.draw_modal())
        out.append(f"\x1b[{self.height};1H")
        out.append(self.draw_status())
        out.append("\x1b[?2026l")
        self.term.write("".join(out))

    def draw_tree(self, width: int) -> list[str]:
        rows = self.tree_rows()
        h = self.body_h - 1
        self.tree_cur = self.clamp(self.tree_cur, 0, len(rows) - 1)
        if self.tree_free:
            pass
        elif self.tree_cur < self.tree_top:
            self.tree_top = self.tree_cur
        elif self.tree_cur >= self.tree_top + h:
            self.tree_top = self.tree_cur - h + 1
        self.tree_top = self.clamp(self.tree_top, 0, max(0, len(rows) - h))

        added = sum(f.added for f in self.files)
        deleted = sum(f.deleted for f in self.files)
        title = LineBuf(width)
        noun = "file" if len(self.files) == 1 else "files"
        title.add(f" {len(self.files)} {noun} ", Style(bold=True))
        title.add(f"+{added} ", Style(fg=role("diff.add.accent")))
        title.add(f"-{deleted}", Style(fg=role("diff.del.accent")))
        title.fill(PLAIN)
        lines = [title.render()]

        current = self.current_page()
        status_colors = {
            "A": "state.success",
            "D": "state.error",
            "M": "accent.info",
            "R": "accent.link",
            "C": "accent.link",
        }
        for i in range(self.tree_top, self.tree_top + h):
            buf = LineBuf(width)
            if i >= len(rows):
                lines.append(buf.render() + " " * width)
                continue
            depth, node = rows[i]
            bg = None
            if i == self.tree_cur and self.focus == "tree":
                bg = role("surface.overlay")
            elif self.node_page(node) == current:
                bg = role("surface.raised")
            base = Style(bg=bg)
            buf.add(" ", base)
            guide = base._replace(fg=role("text.faint"))
            buf.add(tree_guides(node, depth), guide)
            if node.is_dir:
                arrow = "▾ " if node.expanded else "▸ "
                color = "state.warning" if node.commit else "file.dir"
                style = Style(fg=role(color), bg=bg, bold=True)
                if node.commit and self.approved(node.rank):
                    style = NEON_TEXT._replace(bg=bg)
                buf.add(arrow, style)
                name = node.name if node.commit else node.name + "/"
                buf.add_clipped(name, style, width - buf.col)
                if node.commit and node.rank >= 0:
                    self.draw_commit_node(buf, node.rank, bg)
            elif node.message is not None:
                style = Style(fg=role("state.warning"), bg=bg, bold=True)
                buf.add("≡ ", style)
                name_style = Style(bg=bg, bold=self.node_page(node) == current)
                buf.add_clipped(node.name, name_style, width - buf.col)
            else:
                f = self.files[node.file]
                buf.add(
                    f.status + " ",
                    Style(
                        fg=role(status_colors.get(f.status, "text.muted")),
                        bg=bg,
                        bold=True,
                    ),
                )
                counts = f" +{f.added} -{f.deleted}" if not f.binary else ""
                room = width - buf.col
                name_style = Style(bg=bg, bold=self.node_page(node) == current)
                if len(node.name) + len(counts) + 1 <= room:
                    buf.add(node.name, name_style)
                    buf.fill(base, width - len(counts) - 1)
                    buf.add(counts, Style(fg=role("text.faint"), bg=bg))
                else:
                    buf.add_clipped(node.name, name_style, room)
            buf.fill(base)
            lines.append(buf.render())
        return lines

    def draw_commit_node(self, buf: LineBuf, ci: int, bg: Color) -> None:
        """A commit's review badge, then as much of its subject as fits."""
        if self.approved(ci):
            buf.add(" ", Style(bg=bg))
            buf.add("✓", NEON_CHIP)
        if (badge := self.commit_badge(ci)) and "●" in badge[0]:
            text, color = badge
            text = text.lstrip("✓")
            buf.add(" " + text, Style(fg=role(color), bg=bg, bold=True))
        subject = self.commits[ci].subject
        if subject and self.review is not None:
            muted = Style(fg=role("text.muted"), bg=bg)
            if buf.width - buf.col > 4:
                buf.add(" ", muted)
                buf.add_clipped(subject, muted, buf.width - buf.col)

    # the keys, in a box over the diff

    def help_lines(self) -> list[str]:
        return HELP.rstrip("\n").splitlines()

    def help_box(self) -> tuple[int, int, int, int]:
        """Left, top, width and the rows of text inside the box."""
        widest = max(len(line) for line in self.help_lines())
        width = min(widest + 6, self.width - 2)
        rows = min(len(self.help_lines()), self.body_h - 2)
        return (
            (self.width - width) // 2,
            (self.body_h - rows - 2) // 2,
            width,
            rows,
        )

    def help_scroll(self, delta: int) -> None:
        rows = self.help_box()[3]
        most = max(0, len(self.help_lines()) - rows)
        self.help_top = self.clamp(self.help_top + delta, 0, most)

    def help_key(self, key: str) -> None:
        rows = self.help_box()[3]
        steps = {
            "j": 1,
            "down": 1,
            "C-n": 1,
            "C-e": 1,
            "k": -1,
            "up": -1,
            "C-p": -1,
            "C-y": -1,
            "C-d": rows // 2,
            "C-u": -(rows // 2),
            "C-f": rows,
            " ": rows,
            "pgdn": rows,
            "C-b": -rows,
            "pgup": -rows,
            "g": -(10**6),
            "G": 10**6,
        }
        if key in steps:
            self.help_scroll(steps[key])
        else:
            self.show_help = False

    def draw_modal(self) -> str:
        left, top, width, rows = self.help_box()
        bg = role("surface.raised")
        edge = Style(fg=role("accent.primary"), bg=bg)
        lines = self.help_lines()
        more = len(lines) - rows
        title = " keys "
        foot = " j k scroll · any other key closes "
        if more > 0:
            pct = 100 * self.help_top // more
            foot = f" {pct}%{foot}"
        out = []

        def border(left_ch: str, label: str, right_ch: str) -> str:
            buf = LineBuf(width)
            buf.add(left_ch + "─", edge)
            buf.add_clipped(label, edge._replace(bold=True), width - 4)
            while buf.col < width - 1:
                buf.add("─", edge)
            buf.add(right_ch, edge)
            return buf.render()

        out.append(border("╭", title, "╮"))
        for text in lines[self.help_top : self.help_top + rows]:
            buf = LineBuf(width)
            buf.add("│ ", edge)
            heading = text and not text.startswith(" ")
            style = (
                Style(bg=bg, bold=True, fg=role("state.warning"))
                if heading
                else Style(bg=bg)
            )
            buf.add_clipped(" " + text, style, width - 4)
            buf.fill(Style(bg=bg), width - 2)
            buf.add(" │", edge)
            out.append(buf.render())
        out.append(border("╰", foot, "╯"))
        return "".join(
            f"\x1b[{top + y + 1};{left + 1}H{line}"
            for y, line in enumerate(out)
        )

    def draw_diff(self, width: int) -> list[str]:
        lines = []
        commit = self.pinned_commit()
        if commit is not None:
            bg = role("surface.raised")
            buf = LineBuf(width)
            self.draw_commit_head(buf, commit, Style(bg=bg), commit.subject)
            buf.fill(Style(bg=bg))
            lines.append(buf.render())
        hi = self.span[1]
        for i in range(self.top, self.top + self.view_h):
            buf = LineBuf(width)
            if i <= hi:
                self.draw_row(buf, self.rows[i], i == self.cur)
            buf.fill(PLAIN)
            lines.append(buf.render())
        return lines

    def draw_commit_head(
        self, buf: LineBuf, commit: Commit, base: Style, subject: str = ""
    ) -> None:
        """sha, author and date on one line, the subject after them if any."""
        muted = base._replace(fg=role("text.muted"))
        buf.add("  ", base)
        ci = next((i for i, c in enumerate(self.commits) if c is commit), -1)
        if self.approved(ci):
            self.add_approved(buf)
            buf.add(" ", base)
        buf.add(
            commit.sha[:7], base._replace(fg=role("state.warning"), bold=True)
        )
        for part, style in (
            (commit.author, base),
            (relative_date(commit.date), muted),
        ):
            if part:
                buf.add(" · ", muted)
                buf.add(part, style)
        if commit.refs:
            buf.add(
                "  (" + commit.refs + ")",
                base._replace(fg=role("accent.link")),
            )
        if subject:
            buf.add(" · ", muted)
            buf.add_clipped(
                subject, base._replace(bold=True), buf.width - buf.col
            )

    def draw_row(self, buf: LineBuf, row: Row, is_cur: bool) -> None:
        f = self.files[row.file] if row.file >= 0 else None
        primary = (
            role("accent.primary")
            if self.focus == "diff"
            else role("text.faint")
        )
        sign = Style(fg=primary)

        def sign_col(bg: Color = None) -> None:
            buf.add("▌" if is_cur else " ", sign._replace(bg=bg))

        match row.kind:
            case "file":
                bg, fg = role("diff.meta.bg"), role("diff.meta.fg")
                sign_col(bg)
                base = Style(fg=fg, bg=bg, bold=True)
                status = {
                    "A": "added",
                    "D": "deleted",
                    "R": "renamed",
                    "C": "copied",
                }
                buf.add(" ", base)
                buf.add(f.label, base)
                if f.path in self.folded:
                    buf.add("  (folded)", base._replace(bold=False))
                buf.add("  ", base)
                if f.status in status:
                    buf.add(status[f.status] + "  ", base._replace(bold=False))
                buf.add(
                    f"+{f.added}", base._replace(fg=role("diff.add.accent"))
                )
                buf.add(" ", base)
                buf.add(
                    f"-{f.deleted}", base._replace(fg=role("diff.del.accent"))
                )
                buf.fill(base)
            case "meta":
                sign_col()
                buf.add(
                    " " * (self.num_width * 2 + 3) + row.text,
                    Style(fg=role("text.muted")),
                )
            case "commit":
                sign_col()
                if row.tone == "head":
                    commit = self.commits[row.hunk]
                    self.draw_commit_head(buf, commit, PLAIN)
                    return
                style = {
                    "subject": Style(bold=True),
                    "dim": Style(fg=role("text.muted")),
                }.get(row.tone, PLAIN)
                buf.add("  " + row.text, style)
            case "hunk":
                bg = role("diff.frag.bg")
                sign_col(bg)
                base = Style(fg=role("diff.frag.fg"), bg=bg)
                buf.add(" " + f.hunks[row.hunk].header, base)
                buf.fill(base)
            case "line":
                self.draw_code(buf, row, is_cur, sign_col)
            case "note":
                self.draw_note(buf, row, is_cur, sign_col)

    def draw_code(
        self, buf: LineBuf, row: Row, is_cur: bool, sign_col
    ) -> None:
        f = self.files[row.file]
        line = f.hunks[row.hunk].lines[row.line]
        bg = {
            "+": role("diff.add.bg"),
            "-": role("diff.del.bg"),
        }.get(line.kind)
        if bg is None and is_cur:
            bg = role("surface.raised")
        sign_col(bg)

        w = self.num_width
        gutter = Style(fg=role("text.faint"), bg=bg)
        if is_cur:
            gutter = Style(fg=role("accent.primary"), bg=bg, bold=True)
        old = "" if line.old is None else str(line.old)
        new = "" if line.new is None else str(line.new)
        buf.add(f"{old:>{w}} {new:>{w}} ", gutter)
        marker_color = {"+": "diff.add.accent", "-": "diff.del.accent"}.get(
            line.kind
        )
        marker = line.kind if line.kind in "+-" else " "
        buf.add(
            marker + " ",
            Style(
                fg=role(marker_color) if marker_color else None,
                bg=bg,
                bold=True,
            ),
        )

        base = Style(bg=bg)
        if line.kind == "\\":
            base = base._replace(fg=role("text.faint"))
        chars = [base] * len(line.text)

        hl = self.highlight(row.file)
        pos = 0
        for ttype, value in hl.tokens.get((row.hunk, row.line), []):
            color = token_color(ttype)
            if color is not None:
                for k in range(pos, min(pos + len(value), len(chars))):
                    chars[k] = chars[k]._replace(fg=color)
            pos += len(value)
        emph_bg = role(
            "diff.add.emph" if line.kind == "+" else "diff.del.emph"
        )
        for start, end in hl.emph.get((row.hunk, row.line), []):
            for k in range(start, min(end, len(chars))):
                chars[k] = chars[k]._replace(bg=emph_bg)
        if self.search:
            match_style = Style(
                fg=role("text.inverse"), bg=role("state.warning")
            )
            for m in self.search[0].finditer(line.text):
                for k in range(m.start(), m.end()):
                    chars[k] = match_style

        cells = expand(list(zip(line.text, chars)))
        col = 0
        for ch, cw, st in cells:
            if col < self.hscroll:
                if col + cw > self.hscroll:
                    for _ in range(col + cw - self.hscroll):
                        buf.put(" ", 1, st)
                col += cw
                continue
            if not buf.put(ch, cw, st):
                break
            col += cw
        buf.fill(base)

    def draw_prompt_text(
        self, buf: LineBuf, text: str, pos: int, base: Style
    ) -> None:
        """The line with its cursor, scrolled so the cursor shows."""
        room = buf.width - buf.col - 1
        start = 0
        while start < pos and sum(map(cwidth, text[start:pos])) > room - 2:
            start += 1
        if start:
            buf.add("…", base._replace(fg=role("text.faint")))
        buf.add(text[start:pos], base)
        under = text[pos : pos + 1] or " "
        buf.add(under, base._replace(rev=True))
        buf.add(text[pos + 1 :], base)

    def draw_status(self) -> str:
        bg = role("surface.overlay")
        base = Style(fg=role("text.normal"), bg=bg)
        buf = LineBuf(self.width)
        if self.prompt is not None:
            kind, text = self.prompt
            label = NOTE_PROMPTS.get(kind, kind)
            buf.add(label, base._replace(bold=kind in NOTE_PROMPTS))
            self.draw_prompt_text(buf, text, self.prompt_pos, base)
            buf.fill(base)
            return buf.render()

        mode = " TREE " if self.focus == "tree" else " DIFF "
        buf.add(mode, Style(fg=role("accent.primary"), bold=True, rev=True))
        buf.add(" ", base)
        if self.review is not None and self.approved(
            self.current_commit() if self.current_commit() is not None else -1
        ):
            self.add_approved(buf)
            buf.add(" ", base)
        row = self.rows[self.cur]
        lo, hi = self.span
        pct = 100 * (self.cur - lo) // max(1, hi - lo)
        text, style = self.message
        if row.file < 0:
            commit = self.commits[row.hunk]
            where = f"commit {row.hunk + 1}/{len(self.commits)}"
            if not text and row.kind == "commit" and row.tone == "head":
                text = " ".join([commit.sha, commit.author, commit.date])
            text = text or commit.title
        else:
            fi = row.file
            hunks = [r for r in self.rows if r.kind == "hunk" and r.file == fi]
            hunk_no = (
                row.hunk + 1 if row.kind in ("hunk", "line", "note") else 0
            )
            where = (
                f"hunk {hunk_no}/{len(hunks)}  file {fi + 1}/{len(self.files)}"
            )
            text = text or self.files[fi].label
        if not self.message[0]:
            style = base
        if self.unified != self.base_context:
            where = f"{'full' if self.full else f'U{self.context}'}  {where}"
        if summary := self.review_summary():
            where = f"{summary}  {where}"
        right = f" {self.count or self.pending}  {where}  {pct}% "
        room = self.width - buf.col - len(right)
        buf.add_clipped(text, style._replace(bg=bg), max(1, room))
        buf.fill(base, self.width - len(right))
        buf.add(right, base)
        buf.fill(base)
        return buf.render()
