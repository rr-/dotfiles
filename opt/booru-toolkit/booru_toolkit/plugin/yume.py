import asyncio
import json
import urllib.parse
from typing import Any, Optional, Tuple, List, Dict, AsyncIterable
from tempfile import TemporaryFile
import requests
from booru_toolkit import errors
from booru_toolkit.util import bidict
from booru_toolkit.plugin.base import PluginBase
from booru_toolkit.plugin.base import Post
from booru_toolkit.plugin.base import Safety


Json = Any
_SAFETY_MAP = bidict({
    Safety.Safe: 'safe',
    Safety.Questionable: 'sketchy',
    Safety.Explicit: 'unsafe',
})


def _result_to_post(result: Json) -> Post:
    post = Post(
        post_id=result['id'],
        safety=_SAFETY_MAP.inverse[result['safety']],
        tags=result['tags'],
        site_url='https://yume.pl/post/{}'.format(result['id']),
        content_url=result['contentUrl'],
        width=result['canvasWidth'],
        height=result['canvasHeight'],
        source=result['source'],
        title=None
    )
    setattr(post, 'version', result['version'])
    return post


def _process_response(response: requests.Response) -> Json:
    result = json.loads(response.text)
    if response.status_code == 404:
        raise errors.NotFoundError(result['description'])
    if response.status_code != 200:
        raise errors.ApiError(result['description'])
    return result


class PluginYume(PluginBase):
    name = 'yume'

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers['Accept'] = 'application/json'
        self._tag_cache: Dict[str, Dict] = {}

    async def login(self, user_name: str, password: str) -> None:
        self._session.auth = (user_name, password)
        await self._get('/user/' + user_name + '?bump-login')

    async def find_exact_post(self, content: bytes) -> Optional[Post]:
        result = await self._get_similar_posts(content)
        if not result['exactPost']:
            return None
        return _result_to_post(result['exactPost'])

    async def find_similar_posts(
            self, content: bytes) -> List[Tuple[float, Post]]:
        result = await self._get_similar_posts(content)
        return [
            (item['distance'], _result_to_post(item['post']))
            for item in result['similarPosts']]

    async def find_posts(self, query: str) -> AsyncIterable[Post]:
        offset = 0
        while True:
            response = await self._get(
                '/posts?query={}&fields={}&offset={}'.format(
                    urllib.parse.quote(query),
                    ','.join([
                        'id',
                        'source',
                        'safety',
                        'tags',
                        'contentUrl',
                        'canvasWidth',
                        'canvasHeight',
                        'version',
                    ]),
                    offset))
            if not response['results']:
                break
            offset += len(response['results'])
            for result in response['results']:
                yield _result_to_post(result)

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
        with TemporaryFile() as handle:
            handle.write(content)
            handle.seek(0)
            result = await self._post(
                '/posts',
                files={
                    'content': handle,
                    'metadata': json.dumps({
                        'source': source,
                        'safety': _SAFETY_MAP[safety],
                        'anonymous': False,
                        'tags': tags,
                    }),
                })
            return _result_to_post(result)

    async def update_post_tags(self, post: Post, tags: List[str]) -> None:
        await self._put(
            '/post/{}'.format(post.id),
            data={
                'version': getattr(post, 'version'),
                'tags': tags,
            })

    async def find_tags(self, query: str) -> List[str]:
        if not query:
            return []
        response = await self._get(
            '/tags?query={}&limit=20'.format(
                urllib.parse.quote(
                    '*{}* sort:usages,desc'.format('*'.join(query)))))
        return [
            name
            for tag in response['results']
            for name in tag['names']
        ]

    async def tag_exists(self, tag_name: str) -> bool:
        try:
            await self._get_tag(tag_name)
            return True
        except errors.NotFoundError:
            return False

    async def get_tag_implications(self, tag_name: str) -> List[str]:
        try:
            return (await self._get_tag(tag_name))['implications']
        except (errors.NotFoundError, KeyError):
            return []

    async def _get_tag(self, tag_name: str) -> Json:
        cache_key = tag_name.lower()
        if cache_key in self._tag_cache:
            return self._tag_cache[cache_key]
        tag = await self._get('/tag/{}'.format(urllib.parse.quote(tag_name)))
        self._tag_cache[cache_key] = tag
        return tag

    # TODO: memoize
    async def _get_similar_posts(self, content: bytes) -> Json:
        with TemporaryFile() as handle:
            handle.write(content)
            handle.seek(0)
            return await self._post(
                '/posts/reverse-search',
                files={'content': handle})

    async def _get(self, url: str) -> Json:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._session.get(
                    'https://yume.pl/api/' + url.lstrip('/'))))

    async def _put(
            self,
            url: str,
            data: Optional[Dict] = None,
            files: Optional[Dict] = None) -> Json:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._session.put(
                    'https://yume.pl/api/' + url.lstrip('/'),
                    data=(
                        json.dumps(data).encode('utf-8')
                        if data is not None
                        else None),
                    files=files)))

    async def _post(
            self,
            url: str,
            data: Optional[Dict] = None,
            files: Optional[Dict] = None) -> Dict:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._session.post(
                    'https://yume.pl/api/' + url.lstrip('/'),
                    data=(
                        json.dumps(data).encode('utf-8')
                        if data is not None
                        else None),
                    files=files)))
