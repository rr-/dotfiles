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
from diffview.review import Review, make_anchor, place
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

    def test_commit_comment(self) -> None:
        cid = self.store.add("me", "split", commit_title="Add two lines")
        self.assertEqual(self.where(cid), ("commit", 0))


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
        self.assertTrue(self.store.approvals["Add two lines"])
        self.assertEqual(len(self.store.threads()), 2)
        self.assertEqual(app.review_summary(), "2 open  ✓1/1")

        self.keys(app, "z", "u")
        self.assertTrue(any(r.kind == "note" for r in app.rows))
        self.keys(app, "]", "n", "x", "]", "n", "x")
        self.assertFalse(any(r.kind == "note" for r in app.rows))

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
