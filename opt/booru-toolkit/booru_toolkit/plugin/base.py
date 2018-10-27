from enum import Enum
from typing import Optional, Tuple, List, AsyncIterable
from booru_toolkit.plugin.tag_cache import TagCache


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
        title: Optional[str] = None,
    ) -> None:
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
        raise NotImplementedError("Not implemented")

    def __init__(self):
        self._tag_cache = TagCache(self.name)

    async def login(self, user_name: str, password: str) -> None:
        await self._login(user_name, password)
        await self._update_tag_cache()

    async def _login(self, user_name: str, password: str) -> None:
        raise NotImplementedError("Not implemented")

    async def find_exact_post(self, content: bytes) -> Optional[Post]:
        raise NotImplementedError("Not implemented")

    async def find_similar_posts(
        self, content: bytes
    ) -> List[Tuple[float, Post]]:
        raise NotImplementedError("Not implemented")

    async def find_posts(self, query: str) -> AsyncIterable[Post]:
        raise NotImplementedError("Not implemented")

    async def get_post_content(self, post: Post) -> bytes:
        raise NotImplementedError("Not implemented")

    async def upload_post(
        self,
        content: bytes,
        source: Optional[str],
        safety: Safety,
        tags: List[str],
        anonymous: bool,
    ) -> Optional[Post]:
        raise NotImplementedError("Not implemented")

    async def update_post(
        self, post_id: int, safety: Safety, tags: List[str]
    ) -> None:
        raise NotImplementedError("Not implemented")

    async def find_tags(self, query: str) -> List[str]:
        return await self._tag_cache.find_tags(query)

    async def tag_exists(self, tag_name: str) -> bool:
        return await self._tag_cache.tag_exists(tag_name)

    async def get_tag_real_name(self, tag_name: str) -> Optional[str]:
        return await self._tag_cache.get_tag_real_name(tag_name)

    async def get_tag_usage_count(self, tag_name: str) -> int:
        return await self._tag_cache.get_tag_usage_count(tag_name)

    async def get_tag_implications(self, tag_name: str) -> AsyncIterable[str]:
        async for tag in self._tag_cache.get_tag_implications(tag_name):
            yield tag

    async def _update_tag_cache(self) -> None:
        raise NotImplementedError("Not implemented")
