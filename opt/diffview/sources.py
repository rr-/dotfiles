"""Where the units of a review come from, beside git log's commits.

A source hands the viewer files to show at once, and fills them in as it
goes: TreeSource lists a tree at a revision, every file of it one unit
called "tree", then reads the files' contents on a thread of its own and
wakes the viewer as each arrives. A file the viewer asks for comes next.
"""

import subprocess
import threading
from collections.abc import Callable

from .model import Commit, FileDiff, Hunk, Line

BINARY_SNIFF = 8000  # as git, a NUL this early makes a file binary


def whole_file(f: FileDiff, data: bytes) -> None:
    """Fill a listed file with its content, every line a context line."""
    f.meta = []
    if b"\0" in data[:BINARY_SNIFF]:
        f.binary = True
        f.meta.append("binary file")
        return
    text = data.decode(errors="replace")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        f.meta.append("empty file")
        return
    hunk = Hunk("", 1)
    hunk.lines = [Line(" ", ln, n, n, n) for n, ln in enumerate(lines, 1)]
    f.hunks = [hunk]
    f.added = len(lines)


class TreeSource:
    def __init__(self, rev: str, paths: list[str]) -> None:
        self.rev = rev
        self.paths = paths
        self.lock = threading.Lock()
        self.wanted: list[int] = []  # asked for, first in line
        self.ready: list[tuple[int, bytes]] = []
        self.thread: threading.Thread | None = None
        self.done = 0

    def listing(self) -> tuple[list[FileDiff], list[Commit]]:
        """The tree's files, empty for now, and the one unit they are."""
        proc = subprocess.run(
            ["git", "ls-tree", "-r", "-z", self.rev, "--", *self.paths],
            capture_output=True,
        )
        if proc.returncode:
            raise SystemExit(proc.stderr.decode(errors="replace").strip())
        self.blob_by_path: dict[str, str] = {}
        files: list[FileDiff] = []
        for entry in proc.stdout.decode(errors="replace").split("\0"):
            meta, _, path = entry.partition("\t")
            parts = meta.split()
            if len(parts) != 3 or parts[1] != "blob":
                continue  # a submodule, or the empty end
            f = FileDiff(path, path, status="·", commit=0, whole=True)
            f.meta = ["loading…"]
            files.append(f)
            self.blob_by_path[path] = parts[2]
        label = " ".join(["tree", self.rev, *self.paths])
        unit = Commit([label], unit="tree")
        return files, [unit]

    # reading

    def order(self, files: list[FileDiff]) -> None:
        """Read in the order the viewer shows the files, not git's."""
        self.files = files
        self.queue = list(range(len(files)))
        self.blob_of = {
            fi: self.blob_by_path[f.path] for fi, f in enumerate(files)
        }

    def start(self, files: list[FileDiff], wake: Callable[[], None]) -> None:
        self.order(files)
        self.wake = wake
        self.thread = threading.Thread(target=self.read_all, daemon=True)
        self.thread.start()

    def want(self, fi: int) -> None:
        with self.lock:
            if fi in self.queue:
                self.wanted.append(fi)

    def next_file(self) -> int | None:
        with self.lock:
            while self.wanted:
                fi = self.wanted.pop()
                if fi in self.queue:
                    self.queue.remove(fi)
                    return fi
            return self.queue.pop(0) if self.queue else None

    def read_all(self) -> None:
        proc = subprocess.Popen(
            ["git", "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        try:
            while (fi := self.next_file()) is not None:
                proc.stdin.write(self.blob_of[fi].encode() + b"\n")
                proc.stdin.flush()
                header = proc.stdout.readline().split()
                size = int(header[2]) if len(header) == 3 else 0
                data = proc.stdout.read(size)
                proc.stdout.read(1)  # the newline after the content
                with self.lock:
                    self.ready.append((fi, data))
                self.wake()
        finally:
            proc.stdin.close()
            proc.wait()

    def take(self) -> list[int]:
        """Fill in what has arrived since. Gives the files filled."""
        with self.lock:
            ready, self.ready = self.ready, []
        for fi, data in ready:
            whole_file(self.files[fi], data)
        self.done += len(ready)
        return [fi for fi, _ in ready]

    def load_all(self, files: list[FileDiff]) -> None:
        """Everything at once, for a command with no screen to update."""
        self.order(files)
        self.wake = lambda: None
        self.read_all()
        self.take()

    @property
    def loading(self) -> bool:
        return self.done < len(self.blob_by_path)

    def progress(self) -> str:
        return f"loading {self.done}/{len(self.blob_by_path)}"
