"""Running git."""

import re
import subprocess
from pathlib import Path


def initial_context(git_args: list[str] | None) -> int:
    """The -U the diff was made with, as far as we can tell."""
    args = git_args or []
    if "--" in args:
        args = args[: args.index("--")]
    for arg in reversed(args):
        if m := re.fullmatch(r"(?:-U|--unified=)(\d+)", arg):
            return int(m[1])
    proc = subprocess.run(
        ["git", "config", "--get", "diff.context"],
        capture_output=True,
        text=True,
    )
    return int(proc.stdout) if proc.stdout.strip().isdigit() else 3


def git_root() -> Path | None:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    return Path(proc.stdout.strip()) if proc.returncode == 0 else None


class GitError(Exception):
    """git failed: the message is what it wrote to stderr."""


def run_git(cmd: str, args: list[str]) -> str:
    """The output of git diff, or git log -p, as plain text."""
    proc = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            cmd,
            "--no-color",
            "--no-ext-diff",
            "--src-prefix=a/",
            "--dst-prefix=b/",
            *args,
        ],
        capture_output=True,
    )
    if proc.returncode not in (0, 1):
        message = proc.stderr.decode(errors="replace").strip()
        raise GitError(message or f"git {cmd} exited with {proc.returncode}")
    return proc.stdout.decode(errors="replace")


def git_common_dir() -> Path:
    """The .git shared by every worktree of the repository."""
    proc = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
    )
    if proc.returncode:
        raise SystemExit("not in a git repository")
    return Path(proc.stdout.strip())


def default_base() -> str:
    for ref in ("origin/HEAD", "origin/main", "origin/master", "main"):
        proc = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
            capture_output=True,
        )
        if proc.returncode == 0:
            return ref
    raise SystemExit("no base branch found: pass a range like main..HEAD")


def review_range(arg: str | None) -> str:
    """A range as given, or a branch (HEAD by default) since the base."""
    if arg and ".." in arg:
        return arg
    tip = arg or "HEAD"
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{tip}^{{commit}}"],
        capture_output=True,
    )
    if proc.returncode:
        raise SystemExit(f"no branch or commit named {tip}")
    return f"{default_base()}..{tip}"


def range_branch(rng: str) -> str:
    """The branch a range reviews: its tip, HEAD named as its branch."""
    _, _, tip = rng.partition("..")
    tip = tip.lstrip(".") or "HEAD"
    if tip == "HEAD":
        proc = subprocess.run(
            ["git", "symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True,
            text=True,
        )
        tip = proc.stdout.strip() or "HEAD"
    return tip.removeprefix("refs/heads/")


def range_base(rng: str) -> str:
    base, _, _ = rng.partition("..")
    return base or "HEAD"


def titles_in(rev: str) -> set[str]:
    """The subject of every commit reachable from rev."""
    proc = subprocess.run(
        ["git", "log", "--format=%s", rev, "--"],
        capture_output=True,
        text=True,
    )
    return set(proc.stdout.splitlines()) if proc.returncode == 0 else set()


def log_args(rng: str) -> list[str]:
    """git log arguments that show each commit of a range like git show.

    base..tip goes in as base...tip, keeping only commits whose patch is
    not in base yet: one that landed as a copy, by a rebase or squash
    merge, has a sha of its own there and would show again otherwise.
    """
    base, dots, tip = rng.partition("..")
    picks = []
    if dots and not tip.startswith("."):
        rng = f"{base}...{tip}"
        picks = ["--cherry-pick", "--right-only"]
    return [
        "-p",
        "--reverse",
        "--no-merges",
        *picks,
        "--format=medium",
        "--no-decorate",
        rng,
        "--",
    ]
