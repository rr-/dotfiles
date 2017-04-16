from enum import Enum
from pathlib import Path
from typing import Optional, List, Callable
from booru_toolkit.plugin import Safety


def box_to_ui(text: str) -> str:
    return text.replace('_', ' ')


def unbox_from_ui(text: str) -> str:
    return text.replace(' ', '_')


class TagSource(Enum):
    Initial = 0
    UserInput = 1
    Implication = 2


class Tag:
    def __init__(self, name: str, source: TagSource) -> None:
        self.name = name
        self.source = source


class TagList:
    def __init__(self) -> None:
        self._tags: List[Tag] = []
        self.on_update: List[Callable[[], None]] = []

    def get_all(self) -> List[Tag]:
        return sorted(self._tags, key=lambda tag: tag.name)

    def delete(self, tag_to_remove: Tag) -> None:
        self._tags = [
            tag
            for tag in self._tags
            if tag.name.lower() != tag_to_remove.name.lower()
        ]
        self._trigger_update()

    def add(self, name: str, source: TagSource) -> None:
        if any(name.lower() == tag.name.lower() for tag in self._tags):
            return
        self._tags.append(Tag(name, source))
        self._trigger_update()

    def _trigger_update(self) -> None:
        for callback in self.on_update:
            callback()


class UploadSettings:
    def __init__(
            self,
            path: Path,
            safety: Safety,
            source: Optional[str],
            tags: List[str] = []) -> None:
        self.path = path
        self.safety = safety
        self.source = source
        self.tags = TagList()
        for tag_name in tags:
            self.tags.add(tag_name, TagSource.UserInput)

    @property
    def tag_names(self) -> List[str]:
        return [tag.name for tag in self.tags.get_all()]