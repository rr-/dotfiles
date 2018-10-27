import asyncio
import re
import json
from typing import Optional, Tuple, List, Dict, AsyncIterable
import requests
from booru_toolkit import errors
from booru_toolkit import util
from booru_toolkit.plugin.base import PluginBase
from booru_toolkit.plugin.base import Post
from booru_toolkit.plugin.base import Safety


def _process_response(response: requests.Response) -> Dict:
    response.raise_for_status()
    ret = json.loads(response.content)
    if "status" in ret and ret["status"] != "success":
        raise errors.ApiError("Pixiv error ({})".format(ret))
    return ret


class PluginPixiv(PluginBase):
    name = "pixiv"

    def __init__(self) -> None:
        super().__init__()
        self._session = requests.Session()

    async def _login(self, user_name: str, password: str) -> None:
        url = "https://oauth.secure.pixiv.net/auth/token"
        data = {
            "username": user_name,
            "password": password,
            "grant_type": "password",
            "client_id": "bYGKuGVw91e0NMfPGp44euvGt59s",
            "client_secret": "HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
        }
        response = _process_response(self._session.post(url, data=data))
        access_token = response["response"]["access_token"]
        self._session.headers.update(
            {
                # 'User-Agent': 'PixivIOSApp/6.4.0',
                "Referer": "http://www.pixiv.net/",
                "Authorization": "Bearer {}".format(access_token),
            }
        )

    async def find_exact_post(self, content: bytes) -> Optional[Post]:
        return None

    async def find_similar_posts(
        self, content: bytes
    ) -> List[Tuple[float, Post]]:
        return []

    async def find_posts(self, query: str) -> AsyncIterable[Post]:
        match = re.match(r"^artist:(?P<artist_id>\d+)$", query)

        if match:
            artist_id = int(match.group("artist_id"))

            async def page_getter(page: int, page_size: int) -> Dict:
                return await self._get(
                    "/v1/users/{}/works.json".format(artist_id),
                    params={
                        "page": page,
                        "per_page": page_size,
                        "include_stats": True,
                        "include_sanity_level": True,
                        "image_sizes": ",".join(["small", "medium", "large"]),
                        "profile_image_sizes": ",".join([]),
                    },
                )

        else:

            async def page_getter(page: int, page_size: int) -> Dict:
                return await self._get(
                    "/v1/search/works.json",
                    params={
                        "q": query,
                        "page": page,
                        "per_page": page_size,
                        "include_stats": True,
                        "include_sanity_level": True,
                        "image_sizes": ",".join(["small", "medium", "large"]),
                        "profile_image_sizes": ",".join([]),
                    },
                )

        page = 1
        page_size = 50
        while page is not None:
            page_data = await util.retry(5, 1, page_getter, page, 50)

            for item in page_data["response"]:
                base_url = item["image_urls"]["large"]
                for page in range(item["page_count"]):
                    url = base_url.replace("_p0", "_p{}".format(page))
                    yield Post(
                        post_id=item["id"],
                        safety=Safety.Safe,  # TODO
                        tags=item["tags"],
                        site_url=(
                            (
                                "http://www.pixiv.net/member_illust.php"
                                "?mode=medium&illust_id={}"
                            ).format(item["id"])
                        ),
                        content_url=url,
                        width=item["width"],
                        height=item["height"],
                        source=None,
                        title=item["title"],
                    )

            page_size = min(page_size, len(page_data["response"]))
            page = page_data["pagination"]["next"]

    async def get_post_content(self, post: Post) -> bytes:
        return (
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._session.get(post.content_url)
            )
        ).content

    async def upload_post(
        self,
        content: bytes,
        source: Optional[str],
        safety: Safety,
        tags: List[str],
        anonymous: bool,
    ) -> Optional[Post]:
        raise NotImplementedError("Not implemented")

    async def _update_tag_cache(self) -> None:
        pass

    async def update_post(
        self, post_id: int, safety: Safety, tags: List[str]
    ) -> None:
        raise NotImplementedError("Not implemented")

    async def _get(self, url: str, params: Dict) -> Dict:
        return _process_response(
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._session.get(
                    "https://public-api.secure.pixiv.net/" + url.lstrip("/"),
                    params=params,
                ),
            )
        )
