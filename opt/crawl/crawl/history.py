import typing as T
from pathlib import Path


class History:
    def __init__(self) -> None:
        self.visited_urls: T.Set[str] = set()

    def load(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f'"{path}" does not exist')

        self.visited_urls = set(path.read_text().split("\n"))

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.visited_urls))

    def __iter__(self) -> T.Iterable[str]:
        return iter(self.visited_urls)

    def __len__(self) -> int:
        return len(self.visited_urls)

    def __contains__(self, item: T.Any) -> bool:
        return item in self.visited_urls

    def add(self, item: str) -> None:
        self.visited_urls.add(item)

    def remove(self, item: str) -> None:
        self.visited_urls.remove(item)
