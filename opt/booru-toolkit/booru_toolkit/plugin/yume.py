import asyncio
import json
import urllib.parse
from typing import Any, Optional, Tuple, List, Dict, AsyncIterable
from tempfile import TemporaryFile
import requests
from booru_toolkit import util
from booru_toolkit import errors
from booru_toolkit.util import bidict
from booru_toolkit.plugin.base import PluginBase
from booru_toolkit.plugin.base import Post
from booru_toolkit.plugin.base import Safety
from booru_toolkit.plugin.tag_cache import CachedTag


Json = Any
_SAFETY_MAP = bidict({
    Safety.Safe: 'safe',
    Safety.Questionable: 'sketchy',
    Safety.Explicit: 'unsafe',
})
_version_cache: Dict[int, int] = {}


def _result_to_post(result: Json) -> Post:
    post = Post(
        post_id=result['id'],
        safety=_SAFETY_MAP.inverse[result['safety']][0],
        tags=[tag['names'][0] for tag in result['tags']],
        site_url='https://yume.pl/post/{}'.format(result['id']),
        content_url=result['contentUrl'],
        width=result['canvasWidth'],
        height=result['canvasHeight'],
        source=result['source'],
        title=None
    )
    _version_cache[post.id] = result['version']
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
        super().__init__()
        self._session = requests.Session()
        self._session.headers['Accept'] = 'application/json'

    async def _login(self, user_name: str, password: str) -> None:
        self._session.auth = (user_name, password)
        await self._get('/user/' + user_name + '?bump-login=true')

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
            tags: List[str],
            anonymous: bool) -> Optional[Post]:
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
                        'anonymous': anonymous,
                        'tags': tags,
                    }),
                })
            return _result_to_post(result)

    async def update_post(
            self,
            post_id: int,
            safety: Safety,
            tags: List[str]) -> None:
        response = await self._put(
            '/post/{}'.format(post_id),
            data={
                'version': _version_cache[post_id],
                'safety': _SAFETY_MAP[safety],
                'tags': tags,
            })
        _result_to_post(response)

    async def _update_tag_cache(self) -> None:
        if self._tag_cache.exists():
            return
        offset = 0
        limit = 100
        while True:
            print('Downloading tag cache... page {}'.format(offset // limit))
            response = await self._get(
                '/tags?offset={offset}&limit={limit}&fields={fields}'.format(
                    offset=offset,
                    limit=limit,
                    fields=','.join(['names', 'usages', 'implications'])))
            if not response['results']:
                break
            offset += len(response['results'])
            for tag in response['results']:
                for name in tag['names']:
                    self._tag_cache.add(CachedTag(
                        name=name,
                        importance=tag['usages'],
                        implications=tag.get('implications', [])))
        self._tag_cache.save()

    @util.async_lru_cache()
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
