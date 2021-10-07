from collections.abc import Iterable
from pathlib import Path


class History(set[str]):
    def load(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f'"{path}" does not exist')

        self.clear()
        self.update(path.read_text().split("\n"))

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self))
