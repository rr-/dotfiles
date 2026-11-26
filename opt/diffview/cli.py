"""The git-diff-view command."""

import subprocess
import sys

from .app import App
from .gitio import run_git
from .model import ANSI_RE


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
