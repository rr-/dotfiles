import asyncio
import urllib.parse
import xml.dom.minidom
from typing import Optional, Tuple, List, Dict, AsyncIterable
from tempfile import TemporaryFile
import requests
from bs4 import BeautifulSoup
from booru_toolkit import errors
from booru_toolkit.plugin.base import PluginBase
from booru_toolkit.plugin.base import Post
from booru_toolkit.plugin.base import Safety
from booru_toolkit.plugin.tag_cache import CachedTag, TagCache


def _process_response(response: requests.Response) -> str:
    response.raise_for_status()
    return response.content.decode('utf-8')


class PluginGelbooru(PluginBase):
    name = 'gelbooru'

    def __init__(self) -> None:
        self._session = requests.Session()
        self._tag_cache = TagCache(self.name)

    async def login(self, user_name: str, password: str) -> None:
        await self._post(
            '/index.php?page=account&s=login&code=00',
            data={
                'user': user_name,
                'pass': password,
                'submit': 'Log in',
            })
        await self._update_tag_cache()

    async def find_exact_post(self, content: bytes) -> Optional[Post]:
        return None

    async def find_similar_posts(
            self, content: bytes) -> List[Tuple[float, Post]]:
        return []

    async def find_posts(self, query: str) -> AsyncIterable[Post]:
        page = 0
        while True:
            url = (
                '/index.php?page=dapi&s=post&q=index'
                '&limit={limit}&tags={query}&pid={page}'
            ).format(
                query=urllib.parse.quote(query),
                limit=10,
                page=page)

            response = await self._get(url)
            with xml.dom.minidom.parseString(response) as doc:
                posts = doc.getElementsByTagName('post')
                if not posts:
                    break
                for post in posts:
                    yield Post(
                        post_id=int(post.getAttribute('id')),
                        safety={
                            's': Safety.Safe,
                            'q': Safety.Questionable,
                            'e': Safety.Explicit,
                        }[post.getAttribute('rating')],
                        tags=post.getAttribute('tags').split(),
                        site_url=(
                            'http://gelbooru.com/index.php?page=post&s=view'
                            '&id=' + post.getAttribute('id')),
                        content_url='https:' + post.getAttribute('file_url'),
                        width=int(post.getAttribute('width')),
                        height=int(post.getAttribute('height')),
                        source=post.getAttribute('source'),
                        title=None)

            page += 1

    async def get_post_content(self, post: Post) -> bytes:
        return (await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._session.get(post.content_url))).content

    async def upload_post(
            self,
            content: bytes,
            source: Optional[str],
            safety: Safety,
            tags: List[str]) -> Optional[Post]:
        if not tags:
            raise errors.ApiError('No tags given')

        with TemporaryFile() as handle:
            handle.write(content)
            handle.seek(0)

            response = await self._post(
                '/index.php?page=post&s=add',
                data={
                    'tags': ' '.join(tags),
                    'title': '',
                    'source': source or '',
                    'rating': {
                        Safety.Safe: 's',
                        Safety.Questionable: 'q',
                        Safety.Explicit: 'e',
                    }[safety],
                    'submit': 'Upload',
                },
                files={'upload': handle})
            print(response)

            soup = BeautifulSoup(response, 'html.parser')
            content_div = soup.find('div', {'id': 'content'})
            text = content_div.text.lower()
            if 'image added' in text:
                return None
            elif 'already exists' in text:
                raise errors.DuplicateUploadError('Image is already uploaded')
            elif 'generic error' in text:
                raise errors.ApiError('Some fields are missing')
            else:
                raise errors.ApiError('Unknown response from the server')

    async def update_post_tags(self, post: Post, tags: List[str]) -> None:
        raise NotImplementedError('Not supported')

    async def find_tags(self, query: str) -> List[str]:
        return await self._tag_cache.find_tags(query)

    async def tag_exists(self, tag_name: str) -> bool:
        return await self._tag_cache.tag_exists(tag_name)

    async def get_tag_usage_count(self, tag_name: str) -> int:
        return await self._tag_cache.get_tag_usage_count(tag_name)

    async def get_tag_implications(self, tag_name: str) -> AsyncIterable[str]:
        async for tag in self._tag_cache.get_tag_implications(tag_name):
            yield tag

    async def _update_tag_cache(self):
        if self._tag_cache.exists():
            return

        page = 0
        while True:
            print('Downloading tag cache... page {}'.format(page))
            response = await self._get(
                '/index.php?page=dapi&s=tag&q=index&limit={limit}&pid={page}'
                .format(limit=1000, page=page))
            page += 1

            with xml.dom.minidom.parseString(response) as doc:
                tag_wrapper = doc.getElementsByTagName('tags')
                if not tag_wrapper:
                    break
                tags = tag_wrapper[0].getElementsByTagName('tag')
                for tag in tags:
                    name = tag.getAttribute('name')
                    importance = int(tag.getAttribute('count'))
                    if importance > 1:
                        self._tag_cache.add(CachedTag(
                            name=name,
                            importance=importance,
                            implications=[]))
                if not tags:
                    break

        self._tag_cache.save()

    async def _get(self, url: str) -> str:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._session.get,
                'https://gelbooru.com/' + url.lstrip('/')))

    async def _post(
            self,
            url: str,
            data: Optional[Dict] = None,
            files: Optional[Dict] = None) -> str:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._session.post(
                    'http://gelbooru.com/' + url.lstrip('/'),
                    data=data,
                    files=files)))
