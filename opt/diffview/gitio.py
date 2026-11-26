"""Running git."""

import re
import subprocess
import sys
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
        sys.stderr.write(proc.stderr.decode(errors="replace"))
        raise SystemExit(proc.returncode)
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
    return f"{default_base()}..{arg or 'HEAD'}"


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
    """git log arguments that show each commit of a range like git show."""
    return [
        "-p",
        "--reverse",
        "--no-merges",
        "--format=medium",
        "--no-decorate",
        rng,
        "--",
    ]
