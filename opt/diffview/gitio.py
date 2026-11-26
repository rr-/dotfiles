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
