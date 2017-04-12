from enum import Enum
from typing import Optional, Tuple, Set, List, AsyncIterable


class Safety(Enum):
    Safe = 1
    Questionable = 2
    Explicit = 3


class Post:
    def __init__(
            self,
            post_id: int,
            safety: Safety,
            tags: List[str],
            site_url: str,
            content_url: str,
            width: int,
            height: int,
            source: Optional[str],
            title: Optional[str] = None) -> None:
        self.id = post_id
        self.safety = safety
        self.tags = tags
        self.site_url = site_url
        self.content_url = content_url
        self.width = width
        self.height = height
        self.source = source
        self.title = title


class PluginBase:
    @property
    def name(self) -> str:
        raise NotImplementedError('Not implemented')

    async def login(self, user_name: str, password: str) -> None:
        raise NotImplementedError('Not implemented')

    async def find_exact_post(self, content: bytes) -> Optional[Post]:
        raise NotImplementedError('Not implemented')

    async def find_similar_posts(
            self, content: bytes) -> List[Tuple[float, Post]]:
        raise NotImplementedError('Not implemented')

    async def find_posts(self, query: str) -> AsyncIterable[Post]:
        raise NotImplementedError('Not implemented')

    async def get_post_content(self, post: Post) -> bytes:
        raise NotImplementedError('Not implemented')

    async def upload_post(
            self,
            content: bytes,
            source: Optional[str],
            safety: Safety,
            tags: List[str]) -> Optional[Post]:
        raise NotImplementedError('Not implemented')

    async def update_post_tags(self, post: Post, tags: List[str]) -> None:
        raise NotImplementedError('Not implemented')

    async def find_tags(self, query: str) -> List[str]:
        raise NotImplementedError('Not implemented')

    async def tag_exists(self, tag_name: str) -> bool:
        raise NotImplementedError('Not implemented')

    async def get_tag_implications(self, tag_name: str) -> List[str]:
        raise NotImplementedError('Not implemented')

    async def get_tag_implications_recursive(
            self, tag_name: str) -> AsyncIterable[str]:
        to_check = [tag_name]
        visited: Set[str] = set()
        while bool(to_check):
            text = to_check.pop(0)
            if text in visited:
                continue
            visited.add(text)
            for implication in await self.get_tag_implications(text):
                yield implication
                to_check.append(implication)
