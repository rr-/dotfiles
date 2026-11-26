"""The git-diff-view and git-review commands."""

import functools
import subprocess
import sys

from . import review
from .app import App
from .gitio import (
    GitError,
    git_common_dir,
    log_args,
    range_base,
    range_branch,
    review_range,
    run_git,
    titles_in,
)
from .model import ANSI_RE, FileDiff, parse_diff
from .review import REVIEW_FILE, Review
from .session import Session
from .sources import TreeSource


def exit_on_git_error(fn):
    """Say what git said and stop, for a git that fails on the way in."""

    @functools.wraps(fn)
    def run(*args):
        try:
            return fn(*args)
        except GitError as ex:
            raise SystemExit(str(ex))

    return run


@exit_on_git_error
def main() -> None:
    if sys.stdin.isatty():
        git_args: list[str] | None = sys.argv[1:]
        text = run_git("diff", git_args)
    else:
        # As git's pager this gets colored output, and sometimes no diff at
        # all (--stat, --name-only), which goes on to a plain pager instead.
        git_args = None
        raw = sys.stdin.buffer.read()
        text = ANSI_RE.sub("", raw.decode(errors="replace"))

    if not sys.stdout.isatty():
        sys.stdout.write(text)
        return

    app = App(git_args, text)
    if not app.files:
        if git_args is None:
            subprocess.run(["less", "-FRX"], input=raw)
        else:
            print("no changes")
        return
    app.run()


REVIEW_USAGE = """\
usage: git review [<range>]          review commits in the viewer
       git review list [<range>] [--all]
                                     print where the review stands
       git review prune [<range>]    drop what already landed
       git review tree [--list] <rev> [<path>...]
                                     review the files of a tree as they
                                     are, or with --list print where
                                     that review stands

<range> is base..branch, or a branch to take from the default base
(origin/HEAD, origin/main, origin/master or main). HEAD by default.

list prints a line per commit, with its approval and open threads, and
then each open thread (every thread with --all) with where it sits now.

tree shows every file of <rev>, limited to the paths given, whole. Its
comments belong to the paths, not the revision: review the tree at a
later rev and they find their lines again. Files come in as they are
read, the open one first.

prune drops the threads and approvals of commits whose title is in the
range's base but on no commit of the range. git review does it too, each
time it starts; list never changes the file.
"""


@exit_on_git_error
def review_main(argv: list[str]) -> None:
    if argv[:1] in (["-h"], ["--help"], ["help"]):
        print(REVIEW_USAGE)
        print(review.__doc__.strip())
        return
    if argv[:1] == ["list"]:
        args = argv[1:]
        show_all = "--all" in args
        rest = [a for a in args if a != "--all"]
        if len(rest) > 1 or any(a.startswith("-") for a in rest):
            raise SystemExit(REVIEW_USAGE)
        print(review_list(review_range(rest[0] if rest else None), show_all))
        return
    if argv[:1] == ["tree"]:
        args = argv[1:]
        show_list = "--list" in args
        show_all = "--all" in args
        rest = [a for a in args if a not in ("--list", "--all")]
        if not rest or any(a.startswith("-") for a in rest):
            raise SystemExit(REVIEW_USAGE)
        if show_list:
            print(tree_list(rest[0], rest[1:], show_all))
            return
        store = Review(git_common_dir() / REVIEW_FILE)
        app = App(None, "", store, source=TreeSource(rest[0], rest[1:]))
        if not app.files:
            print(f"no files in {' '.join(rest)}")
            return
        app.run()
        return
    if argv[:1] == ["prune"]:
        if len(argv) > 2 or any(a.startswith("-") for a in argv[1:]):
            raise SystemExit(REVIEW_USAGE)
        rng = review_range(argv[1] if len(argv) > 1 else None)
        store = Review(git_common_dir() / REVIEW_FILE)
        print(pruned(store, rng) or "nothing has landed yet")
        return
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        raise SystemExit(REVIEW_USAGE)
    rng = review_range(argv[0] if argv else None)
    store = Review(git_common_dir() / REVIEW_FILE, range_branch(rng))
    args = log_args(rng)
    text = run_git("log", args)
    if not sys.stdout.isatty():
        sys.stdout.write(text)
        return
    notice = pruned(store, rng)
    app = App(args, text, store, "log")
    if notice:
        app.flash(notice, "text.faint")
    if not app.files:
        print(f"no changes in {rng}")
        return
    app.run()


def pruned(store: Review, rng: str) -> str:
    """Drop what landed in the range's base, and say what went."""
    keep = {c.subject for c in parse_diff(run_git("log", log_args(rng)))[1]}
    base = range_base(rng)
    threads, approvals = store.prune(titles_in(base), keep)
    if not threads and not approvals:
        return ""
    what = [
        f"{n} {noun}{'' if n == 1 else 's'}"
        for n, noun in ((threads, "thread"), (approvals, "approval"))
        if n
    ]
    return f"pruned {' and '.join(what)} of commits already in {base}"


def where_now(c: dict, at: tuple, files: list[FileDiff]) -> str:
    if at[0] == "file":
        return f"{c.get('path')}, the whole file"
    if at[0] == "commit":
        return "the whole commit"
    side = f"({c.get('side')})"
    if at[0] == "outdated" and c.get("line_text") is None:
        return f"{c.get('path')}, the whole file, gone from the commit"
    if at[0] == "outdated":
        return f"{c.get('path')}:{c.get('line')} {side}, line gone"
    _, fi, hi, li = at
    line = files[fi].hunks[hi].lines[li]
    number = line.old if c.get("side") == "old" else line.new
    return f"{c.get('path')}:{number} {side}"


def review_list(rng: str, show_all: bool) -> str:
    store = Review(git_common_dir() / REVIEW_FILE, range_branch(rng))
    files, commits = parse_diff(run_git("log", log_args(rng)))
    head = f"review of {rng}, branch {store.branch}, in {store.path}"
    return format_list(Session(store, files, commits), head, show_all)


def tree_list(rev: str, paths: list[str], show_all: bool) -> str:
    store = Review(git_common_dir() / REVIEW_FILE)
    source = TreeSource(rev, paths)
    files, units = source.listing()
    source.load_all(files)
    head = f"review of {units[0].lines[0]}, in {store.path}"
    return format_list(Session(store, files, units), head, show_all)


def format_list(session: Session, head: str, show_all: bool) -> str:
    store, files, commits = session.store, session.files, session.commits
    placed = session.placed

    out = [head, ""]
    if store.bad:
        out += [f"skipped {store.bad} lines that are not records", ""]
    for ci, commit in enumerate(commits):
        n = session.open_threads.get(ci, 0)
        state = session.verdict(ci)
        if state == "changes requested":
            state = "CHANGES REQUESTED, no pull request yet"
        if n:
            state = ", ".join(filter(None, [state, f"{n} open"]))
        name = f"{commit.sha[:10]}  {commit.subject}"
        if commit.unit:
            name = commit.lines[0]
        out.append(f"{name}  [{state or '-'}]")
        for path, verdict in session.file_verdicts_of(ci):
            if verdict == "changes requested":
                verdict = "CHANGES REQUESTED"
            out.append(f"{' ' * 12}{path}  [{verdict}]")
    if elsewhere := session.elsewhere():
        out += ["", f"{elsewhere} open threads are on commits not in it"]

    for ci, commit in enumerate(commits):
        threads = [
            c
            for c in session.threads_of(ci)
            if show_all or store.is_open(c["id"])
        ]
        if not threads:
            continue
        name = commit.lines[0] if commit.unit else ""
        out += ["", f"== {name or commit.sha[:10] + ' ' + commit.subject}"]
        for c in threads:
            status = c.get("status", "open")
            out.append("")
            out.append(
                f"#{c['id']} {status}, on "
                f"{where_now(c, placed[c['id']], files)}"
            )
            if c.get("line_text") is not None:
                out.append(f"  > {c['line_text']}")
            for entry in [c, *store.replies(c["id"])]:
                head = f"  {entry.get('author', '?')}, {entry.get('created')}"
                out.append(f"{head} (#{entry['id']}):")
                for line in str(entry.get("text", "")).splitlines():
                    out.append(f"    {line}")
    return "\n".join(out)
