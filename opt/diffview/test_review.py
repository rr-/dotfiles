"""Tests for review mode. Run from the repository root with

    uv run --no-project --with pygments==2.21.0 \
        --with-editable opt/diffview python -m unittest opt/diffview/test_review.py
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from diffview.app import App
from diffview.gitio import log_args, run_git
from diffview.model import parse_diff
from diffview.prompt import edit_line
from diffview.review import Review, make_anchor, place
from diffview.session import Session
from diffview.term import Mouse

BODY = [f"line {i}" for i in range(1, 21)]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    ).stdout


class FakeTerm:
    fd = -1

    def size(self) -> tuple[int, int]:
        return 120, 40

    def write(self, text: str) -> None:
        pass


class RepoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "commit.gpgsign", "false")
        self.write("a.txt", BODY)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "Base")
        git(self.repo, "switch", "-qc", "topic")
        self.write("a.txt", BODY[:10] + ["new one", "new two"] + BODY[10:])
        git(self.repo, "commit", "-qam", "Add two lines")
        self.old_cwd = os.getcwd()
        os.chdir(self.repo)
        self.store = Review(self.repo / ".git/review.jsonl")

    def tearDown(self) -> None:
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def write(self, name: str, lines: list[str]) -> None:
        (self.repo / name).write_text("\n".join(lines) + "\n")

    def diff(self):
        return parse_diff(run_git("log", log_args("main..topic")))

    def comment_on(self, text: str) -> str:
        files, commits = self.diff()
        hunk = files[0].hunks[0]
        li = next(i for i, ln in enumerate(hunk.lines) if ln.text == text)
        return self.store.add(
            "me",
            "why?",
            commit_title=commits[0].subject,
            **make_anchor(files[0], 0, li),
        )

    def where(self, cid: str) -> tuple:
        files, commits = self.diff()
        at = place(self.store.comments[cid], files, commits)
        if at[0] != "line":
            return at
        line = files[at[1]].hunks[at[2]].lines[at[3]]
        return ("line", line.text, line.new)


class AnchorTests(RepoTest):
    def test_survives_a_rebase_that_moves_the_line(self) -> None:
        cid = self.comment_on("new two")
        self.assertEqual(self.where(cid), ("line", "new two", 12))
        git(self.repo, "switch", "-q", "main")
        self.write("a.txt", ["top"] * 5 + BODY)
        git(self.repo, "commit", "-qam", "Grow the top")
        git(self.repo, "switch", "-q", "topic")
        git(self.repo, "rebase", "-q", "main")
        self.assertEqual(self.where(cid), ("line", "new two", 17))

    def test_a_changed_line_is_outdated(self) -> None:
        cid = self.comment_on("new one")
        self.write("a.txt", BODY[:10] + ["changed", "new two"] + BODY[10:])
        git(self.repo, "commit", "-q", "--amend", "-a", "--no-edit")
        self.assertEqual(self.where(cid), ("outdated", 0))

    def test_a_reworded_commit_is_elsewhere(self) -> None:
        cid = self.comment_on("new one")
        git(self.repo, "commit", "-q", "--amend", "-m", "Other title")
        self.assertEqual(self.where(cid), ("elsewhere",))

    def test_equal_lines_are_told_apart_by_context(self) -> None:
        lines = ["x"] * 3 + ["dup", "a"] + ["x"] * 6 + ["dup", "b"]
        self.write("a.txt", lines)
        git(self.repo, "commit", "-qam", "Dups")
        files, commits = parse_diff(run_git("log", log_args("HEAD~1..HEAD")))
        hunk = files[0].hunks[0]
        second = [
            i
            for i, ln in enumerate(hunk.lines)
            if ln.text == "dup" and ln.kind == "+"
        ][1]
        c = {"commit_title": "Dups", **make_anchor(files[0], 0, second)}
        self.assertEqual(place(c, files, commits), ("line", 0, 0, second))

    def test_a_thread_stays_on_its_branch(self) -> None:
        git(self.repo, "branch", "other")
        self.store.branch = "topic"
        cid = self.comment_on("new one")
        self.assertEqual(self.store.comments[cid]["branch"], "topic")
        reply = self.store.add("claude", "ok", reply_to=cid)
        self.assertNotIn("branch", self.store.comments[reply])
        files, commits = parse_diff(run_git("log", log_args("main..other")))
        c = self.store.comments[cid]
        self.assertEqual(place(c, files, commits, "other"), ("elsewhere",))
        self.assertEqual(place(c, files, commits, "topic")[0], "line")
        old = {k: v for k, v in c.items() if k != "branch"}
        self.assertEqual(place(old, files, commits, "other")[0], "line")

    def test_commit_comment(self) -> None:
        cid = self.store.add("me", "split", commit_title="Add two lines")
        self.assertEqual(self.where(cid), ("commit", 0))


class PromptTests(unittest.TestCase):
    def run_keys(self, text: str, pos: int, *keys: str) -> tuple[str, int]:
        for key in keys:
            text, pos = edit_line(text, pos, key) or (text, pos)
        return text, pos

    def test_words(self) -> None:
        self.assertEqual(
            self.run_keys("foo bar.baz", 11, "M-b"), ("foo bar.baz", 8)
        )
        self.assertEqual(
            self.run_keys("foo bar", 7, "M-b", "M-b"), ("foo bar", 0)
        )
        self.assertEqual(self.run_keys("foo bar", 0, "M-f"), ("foo bar", 3))
        self.assertEqual(
            self.run_keys("foo bar", 7, "M-backspace"), ("foo ", 4)
        )
        self.assertEqual(self.run_keys("foo bar", 0, "M-d"), (" bar", 0))
        self.assertEqual(self.run_keys("a b.c", 5, "C-w"), ("a ", 2))

    def test_insert_and_kill(self) -> None:
        self.assertEqual(self.run_keys("ac", 1, "b"), ("abc", 2))
        self.assertEqual(self.run_keys("abc", 1, "C-k"), ("a", 1))
        self.assertEqual(self.run_keys("abc", 1, "C-u"), ("bc", 0))
        self.assertEqual(self.run_keys("abc", 1, "backspace"), ("bc", 0))
        self.assertEqual(self.run_keys("abc", 1, "delete"), ("ac", 1))
        self.assertIsNone(edit_line("abc", 1, "enter"))


class KeyTests(unittest.TestCase):
    def test_alt_keys_are_not_esc(self) -> None:
        import pty
        import tty

        from diffview.term import Terminal

        master, slave = pty.openpty()
        tty.setraw(slave)
        term = Terminal.__new__(Terminal)
        term.fd, term.buf = slave, b""
        term.wake_r, term.wake_w = os.pipe()
        os.write(master, b"\x1bb\x1b\x7f\x1b[1;5D\x1b")
        keys = [term.read_key() for _ in range(4)]
        self.assertEqual(keys, ["M-b", "M-backspace", "C-left", "esc"])
        for fd in (master, slave, term.wake_r, term.wake_w):
            os.close(fd)


class RangeTests(RepoTest):
    def test_a_commit_that_landed_as_a_copy_is_left_out(self) -> None:
        self.write("b.txt", ["more"])
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "Add b")
        git(self.repo, "switch", "-q", "main")
        git(self.repo, "cherry-pick", "topic~1")
        git(self.repo, "switch", "-q", "topic")
        _, commits = self.diff()
        self.assertEqual([c.subject for c in commits], ["Add b"])


class StoreTests(RepoTest):
    def test_later_lines_update_and_bad_lines_are_skipped(self) -> None:
        cid = self.comment_on("new one")
        with self.store.path.open("a") as handle:
            handle.write("not json\n")
            reply = {"id": "r1", "author": "claude", "reply_to": cid}
            handle.write(json.dumps(reply | {"text": "done"}) + "\n")
            handle.write(json.dumps({"id": "r2", "reply_to": "r1"}) + "\n")
            handle.write(json.dumps({"id": cid, "status": "resolved"}) + "\n")
        self.store.approve("Add two lines", True)
        self.store.approve("Add two lines", False)
        self.store.load()
        self.assertEqual(self.store.bad, 1)
        self.assertFalse(self.store.is_open(cid))
        self.assertEqual(self.store.comments[cid]["text"], "why?")
        self.assertEqual(
            [c["id"] for c in self.store.replies(cid)], ["r1", "r2"]
        )
        self.assertEqual([c["id"] for c in self.store.threads()], [cid])
        self.assertFalse(self.store.approvals["Add two lines"])

    def test_empty_commits_stay_apart(self) -> None:
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "Empty")
        self.write("a.txt", BODY)
        git(self.repo, "commit", "-qam", "Undo")
        _, commits = self.diff()
        self.assertEqual(
            [c.subject for c in commits], ["Add two lines", "Empty", "Undo"]
        )


class SessionTests(RepoTest):
    def session(self) -> Session:
        files, commits = self.diff()
        return Session(self.store, files, commits)

    def line_target(self, s: Session, text: str) -> tuple:
        hunk = s.files[0].hunks[0]
        li = next(i for i, ln in enumerate(hunk.lines) if ln.text == text)
        return ("line", 0, 0, li)

    def test_comments_on_each_target(self) -> None:
        s = self.session()
        line = s.comment(self.line_target(s, "new one"), "a")
        whole_file = s.comment(("file", 0), "b")
        whole = s.comment(("commit", 0), "c")
        rec = self.store.comments
        self.assertEqual(rec[line]["line_text"], "new one")
        self.assertEqual(
            (rec[whole_file]["path"], rec[whole_file]["line_text"]),
            ("a.txt", None),
        )
        self.assertIsNone(rec[whole]["path"])
        for cid in (line, whole_file, whole):
            self.assertEqual(rec[cid]["commit_title"], "Add two lines")
        self.assertEqual(s.placed[line][0], "line")
        self.assertEqual(s.placed[whole_file], ("file", 0))
        self.assertEqual(s.placed[whole], ("commit", 0))
        self.assertEqual(s.open_threads, {0: 3})
        self.assertEqual(s.file_threads, {0: (2, 2)})
        self.assertEqual(
            [c["id"] for c in s.threads_of(0)], [line, whole_file, whole]
        )

    def test_resolve_and_reply(self) -> None:
        s = self.session()
        cid = s.comment(("commit", 0), "split")
        self.assertTrue(s.toggle_resolve(cid))
        self.assertEqual(s.open_threads, {})
        self.assertTrue(s.reply(cid, "no", author="me"))
        self.assertTrue(self.store.is_open(cid))
        self.assertFalse(s.reply(cid, "still no"))
        self.assertEqual(s.open_threads, {0: 1})

    def test_verdicts(self) -> None:
        s = self.session()
        self.assertEqual(s.summary(), (0, 0, 1))
        self.assertEqual(s.toggle_verdict(0, "approved"), "approved")
        self.assertEqual(s.summary(), (0, 1, 1))
        self.assertEqual(
            s.toggle_verdict(0, "changes requested"), "changes requested"
        )
        self.assertEqual(s.verdict(0), "changes requested")
        self.assertEqual(s.toggle_verdict(0, "changes requested"), "")
        self.assertEqual(s.verdict(0), "")

    def test_threads_of_other_branches_are_elsewhere(self) -> None:
        self.store.branch = "other"
        s = self.session()
        s.comment(("commit", 0), "x")
        self.store.branch = "topic"
        s = self.session()
        self.assertEqual(s.open_threads, {})
        self.assertEqual(s.elsewhere(), 1)


class PruneTests(RepoTest):
    def test_drops_what_landed_and_keeps_the_rest(self) -> None:
        landed = self.store.add("me", "old", commit_title="Base")
        self.store.add("claude", "fixed", reply_to=landed)
        self.store.approve("Base", True)
        live = self.store.add("me", "split", commit_title="Add two lines")
        self.store.approve("Add two lines", True)
        mine = self.store.add("me", "both", commit_title="In both")
        with self.store.path.open("a") as handle:
            handle.write("not json\n")
        threads, approvals = self.store.prune(
            {"Base", "In both"}, {"Add two lines", "In both"}
        )
        self.assertEqual((threads, approvals), (1, 1))
        self.assertEqual(
            sorted(c["id"] for c in self.store.threads()), sorted([live, mine])
        )
        self.assertNotIn("Base", self.store.approvals)
        self.assertTrue(self.store.approvals["Add two lines"])
        self.assertIn("not json", self.store.path.read_text())
        self.assertEqual(self.store.prune({"Base"}, set()), (0, 0))

    def test_file_verdicts_go_with_their_commit(self) -> None:
        self.store.approve("Base", True, path="a.txt")
        self.store.approve("Live", True, path="a.txt")
        self.assertEqual(self.store.prune({"Base"}, set()), (0, 1))
        self.assertEqual(self.store.file_verdict("Base", "a.txt"), "")
        self.assertEqual(self.store.file_verdict("Live", "a.txt"), "approved")

    def test_an_append_meanwhile_is_not_lost(self) -> None:
        self.store.add("me", "old", commit_title="Base")
        real_load = self.store.load
        calls = []

        def load_then_append() -> None:
            real_load()
            if not calls:
                calls.append(1)
                with self.store.path.open("a") as handle:
                    handle.write(json.dumps({"id": "late", "text": "hi"}))
                    handle.write("\n")

        self.store.load = load_then_append
        self.store.prune({"Base"}, set())
        self.store.load = real_load
        self.store.load()
        self.assertIn("late", self.store.comments)
        self.assertEqual(self.store.threads()[0]["id"], "late")


class AppTests(RepoTest):
    def app(self) -> App:
        args = log_args("main..topic")
        app = App(args, run_git("log", args), self.store, "log")
        app.term = FakeTerm()
        app.draw()
        return app

    def keys(self, app: App, *keys: str) -> None:
        for key in keys:
            app.handle(key)
            app.draw()

    def goto_text(self, app: App, text: str) -> None:
        app.set_cur(
            next(
                i
                for i, r in enumerate(app.rows)
                if r.kind == "line" and app.row_text(r) == text
            )
        )

    def test_comment_reply_resolve_approve(self) -> None:
        app = self.app()
        self.goto_text(app, "new one")
        self.keys(app, "c", *"looks off", "enter")
        (root,) = self.store.threads()
        self.assertEqual(root["line_text"], "new one")
        self.assertEqual(root["commit_title"], "Add two lines")
        notes = [r for r in app.rows if r.kind == "note"]
        self.assertEqual([r.tone for r in notes], ["head", "body"])

        self.keys(app, "gg", "]", "n")
        self.assertEqual(app.rows[app.cur].note, root["id"])
        self.keys(app, "x")
        self.assertFalse(self.store.is_open(root["id"]))
        self.keys(app, "c", *"no", "enter")
        self.assertTrue(self.store.is_open(root["id"]))
        self.assertEqual(len(self.store.replies(root["id"])), 1)

        self.keys(app, "C", *"split it", "enter", "a")
        self.assertNotIn("Add two lines", self.store.approvals)
        self.keys(app, "<", "M-a")
        self.assertTrue(self.store.approvals["Add two lines"])
        self.assertEqual(len(self.store.threads()), 2)
        self.assertEqual(app.review_summary(), "2 open  ✓1/1")

        self.keys(app, "z", "u")
        self.assertTrue(any(r.kind == "note" for r in app.rows))
        self.keys(app, "]", "n", "x", "]", "n", "x")
        self.assertFalse(any(r.kind == "note" for r in app.rows))

    def test_alt_b_and_esc_keep_the_comment(self) -> None:
        app = self.app()
        self.goto_text(app, "new one")
        self.keys(app, "c", *"fix this", "M-b", "M-b", *"please ", "esc")
        self.assertIsNone(app.prompt)
        self.assertEqual(self.store.threads(), [])
        self.keys(app, "c")
        self.assertEqual(app.prompt, ("comment", "please fix this"))
        self.keys(app, "end", "!", "enter")
        (root,) = self.store.threads()
        self.assertEqual(root["text"], "please fix this!")
        self.assertEqual(app.drafts, {})

    def test_three_states(self) -> None:
        app = self.app()
        title = "Add two lines"
        self.assertEqual(self.store.verdict(title), "")
        self.keys(app, "M-r")
        self.assertEqual(self.store.verdict(title), "changes requested")
        self.keys(app, "M-a")
        self.assertEqual(self.store.verdict(title), "approved")
        self.keys(app, "M-r")
        self.assertEqual(self.store.verdict(title), "changes requested")
        self.keys(app, "M-r")
        self.assertEqual(self.store.verdict(title), "")
        last = json.loads(self.store.path.read_text().splitlines()[-1])
        self.assertEqual(
            (last["approved"], last["changes_requested"]), (False, False)
        )

    def test_a_failed_reload_keeps_the_view_and_says_why(self) -> None:
        app = self.app()
        before = len(app.files)
        git(self.repo, "reset", "-q", "--hard", "main")
        self.keys(app, "r")
        self.assertIn("nothing is left", app.alert[0])
        self.assertEqual(len(app.files), before)
        self.keys(app, "q")
        self.assertIsNone(app.alert)
        git(self.repo, "branch", "-m", "main", "gone")
        self.keys(app, "r")
        self.assertIn("git failed", app.alert[0])
        self.assertTrue(any("main" in line for line in app.alert[1]))
        self.assertEqual(len(app.files), before)

    def test_a_comment_on_the_file_header_stays_with_the_file(self) -> None:
        app = self.app()
        header = next(i for i, r in enumerate(app.rows) if r.kind == "file")
        app.set_cur(header)
        self.keys(app, "c", *"rename it", "enter")
        (root,) = self.store.threads()
        self.assertEqual((root["path"], root["line_text"]), ("a.txt", None))
        files, commits = self.diff()
        self.assertEqual(place(root, files, commits), ("file", 0))
        after = app.rows[header + 1]
        self.assertEqual((after.kind, after.thread), ("note", root["id"]))
        git(self.repo, "checkout", "HEAD~1", "--", "a.txt")
        self.write("c.txt", ["other"])
        git(self.repo, "add", "a.txt", "c.txt")
        git(self.repo, "commit", "-q", "--amend", "--no-edit")
        files, commits = self.diff()
        self.assertEqual(place(root, files, commits)[0], "outdated")

    def test_dot_comma_and_angles_jump(self) -> None:
        self.write("b.txt", ["b"])
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "Add b")
        app = self.app()

        def where() -> tuple:
            return app.pages[app.current_page()]

        self.assertEqual(where(), ("commit", 0))
        self.keys(app, ".")
        self.assertEqual(where(), ("file", 0))
        self.keys(app, ".")
        self.assertEqual(where(), ("file", 1))
        self.keys(app, ",")
        self.assertEqual(where(), ("file", 0))
        self.keys(app, ">")
        self.assertEqual(where(), ("commit", 1))
        self.keys(app, "<")
        self.assertEqual(where(), ("commit", 0))

    def test_files_with_threads_get_a_badge(self) -> None:
        app = self.app()
        self.assertEqual(app.file_badge(0), ("", ""))
        self.goto_text(app, "new one")
        self.keys(app, "c", *"hm", "enter")
        self.assertEqual(app.file_badge(0), (" ●1", "state.warning"))
        self.keys(app, "]", "n", "x")
        self.assertEqual(app.file_badge(0), (" ○", "text.faint"))

    def test_verdicts_go_to_the_file_or_the_commit(self) -> None:
        app = self.app()
        title = "Add two lines"
        self.keys(app, ".", "M-a")
        self.assertEqual(self.store.file_verdict(title, "a.txt"), "approved")
        self.assertEqual(self.store.verdict(title), "")
        self.assertEqual(app.here_verdict(), "approved")
        self.keys(app, "M-r")
        self.assertEqual(
            self.store.file_verdict(title, "a.txt"), "changes requested"
        )
        self.keys(app, "<", "M-a")
        self.assertEqual(self.store.verdict(title), "approved")
        self.assertEqual(
            self.store.file_verdict(title, "a.txt"), "changes requested"
        )
        self.assertEqual(app.here_verdict(), "approved")
        self.keys(app, ".", "M-r")
        self.assertEqual(self.store.file_verdict(title, "a.txt"), "")
        self.assertEqual(self.store.verdict(title), "approved")

    def test_one_commit_still_shows_its_badge(self) -> None:
        self.store.approve("Add two lines", True)
        app = self.app()
        (node,) = [n for n in app.tree.children.values() if n.commit]
        self.assertEqual(app.commit_badge(node.rank), ("✓", "state.success"))

    def test_mouse_and_help(self) -> None:
        app = self.app()
        tree_w = app.tree_width()
        app.mouse(Mouse(0, tree_w + 10, 2, True))
        app.mouse(Mouse(0, tree_w + 10, 2, True))
        self.assertEqual(app.prompt and app.prompt[0], "comment")
        self.keys(app, "esc", ":", "h", "e", "l", "p", "enter")
        self.assertTrue(app.show_help)
        app.draw()
        self.keys(app, "j", "q")
        self.assertFalse(app.show_help)
        app.mouse(Mouse(65, tree_w + 10, 8, True))
        app.mouse(Mouse(64, 2, 3, True))
        app.mouse(Mouse(0, 2, 3, True))
        app.draw()


if __name__ == "__main__":
    unittest.main()
