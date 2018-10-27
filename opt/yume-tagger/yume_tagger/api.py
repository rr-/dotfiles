import json
import functools
import urllib.parse
from typing import Any, Optional, Set, Dict, Iterable
import requests


Post = Dict
Tag = Dict


class ApiError(RuntimeError):
    pass


def _simplify_tag_relations(tag: Dict) -> Dict:
    for key in ['suggestions', 'implications']:
        tag[key] = [rel['names'][0] for rel in tag[key]]
    return tag


def _process_response(response: requests.Response) -> Dict:
    if response.status_code != 200:
        raise ApiError(json.loads(response.text)['description'])
    return json.loads(response.text)


class Api:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers['Content-Type'] = 'application/json'
        self._session.headers['Accept'] = 'application/json'
        self._api_url = 'https://yume.pl/api'

    def login(self, user_name: str, password: str) -> None:
        self._session.auth = (user_name, password)
        self._bump_login(user_name)

    def get_post(self, post_id: int) -> Post:
        return self._get('/post/{}'.format(post_id))

    def update_post(self, post_id: int, data: Post) -> Post:
        return self._put('/post/{}'.format(post_id), data=data)

    @functools.lru_cache()
    def get_tag(self, tag_name: str) -> Tag:
        ret = self._get('/tag/' + tag_name)
        _simplify_tag_relations(ret)
        return ret

    def get_tag_implications(self, tag_name: str) -> Iterable[str]:
        to_check = [tag_name]
        visited: Set[str] = set([tag_name])
        while to_check:
            tag_name = to_check.pop(0)
            try:
                tag = self.get_tag(tag_name)
            except ApiError:
                tag = None
            if tag:
                for implication in tag['implications']:
                    if implication not in visited:
                        yield implication
                        visited.add(implication)
                        to_check.append(implication)

    def find_tags(self, query: str) -> Iterable[Tag]:
        offset = 0
        while True:
            response = self._get(
                '/tags?query={}&offset={}'.format(
                    urllib.parse.quote(query), offset
                )
            )
            if not response['results']:
                break
            offset += len(response['results'])
            for result in response['results']:
                _simplify_tag_relations(result)
                yield result

    def get_last_post_id(self) -> Optional[int]:
        response = self._get('/posts?fields=id')
        results = response['results']
        if not results:
            return None
        return results[0]['id']

    def create_tag(self, tag: Tag) -> Tag:
        ret = self._post('/tags', data=tag)
        _simplify_tag_relations(ret)
        return ret

    def delete_tag(self, tag: Tag) -> None:
        self._delete('/tag/{}'.format(tag['names'][0]), data=tag)

    def update_tag(self, old_tag_name: str, new_tag_data: Tag) -> Tag:
        ret = self._put('/tag/{}'.format(old_tag_name), data=new_tag_data)
        _simplify_tag_relations(ret)
        return ret

    def merge_tags(self, old_tag: Tag, new_tag: Tag) -> Tag:
        return self._post(
            '/tag-merge',
            data={
                'removeVersion': old_tag['version'],
                'remove': old_tag['names'][0],
                'mergeToVersion': new_tag['version'],
                'mergeTo': new_tag['names'][0],
            },
        )

    def _bump_login(self, user_name: str) -> None:
        self._get('/user/{}?bump-login=true'.format(user_name))

    def _get(self, url: str) -> Dict:
        return _process_response(self._session.get(self._api_url + url))

    def _post(self, url: str, data: Any) -> Dict:
        return _process_response(
            self._session.post(
                self._api_url + url, data=json.dumps(data).encode('utf-8')
            )
        )

    def _put(self, url: str, data: Any) -> Dict:
        return _process_response(
            self._session.put(
                self._api_url + url, data=json.dumps(data).encode('utf-8')
            )
        )

    def _delete(self, url: str, data: Any = None) -> Dict:
        return _process_response(
            self._session.delete(
                self._api_url + url, data=json.dumps(data).encode('utf-8')
            )
        )
