import argparse
import asyncio
import dataclasses
import re
import typing as T
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from crawl.cmd.base import BaseCommand

SURE_MEDIA_EXTENSIONS = [".jpg", ".gif", ".png", ".webm"]


@dataclasses.dataclass
class CrawlState:
    args: argparse.Namespace
    visited_urls: T.Set[str] = dataclasses.field(default_factory=set)
    media_urls: T.Set[str] = dataclasses.field(default_factory=set)
    linkings: T.Dict[str, T.Set[str]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ProbeResult:
    url: str
    is_media: bool
    child_urls: T.Set[str] = dataclasses.field(default_factory=set)


def _probe_url(url: str, crawl_state: CrawlState) -> ProbeResult:
    crawl_state.visited_urls.add(url)

    if not url.endswith(tuple(SURE_MEDIA_EXTENSIONS)):
        print("probing", url)

        # TODO: retry mechanism
        response = requests.head(url, timeout=3)
        response.raise_for_status()

        mime = response.headers["content-type"].split(";")[0].lower()
        if mime == "text/html":
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            return ProbeResult(
                url=url,
                is_media=False,
                child_urls=_collect_links(response, crawl_state),
            )

    return ProbeResult(url=url, is_media=True)


def _collect_links(
    response: requests.Response, crawl_state: CrawlState
) -> T.Set[str]:
    ret: T.Set[str] = set()
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        child_url = urllib.parse.urldefrag(
            urllib.parse.urljoin(response.url, link["href"])
        ).url

        if not child_url.startswith("javascript:"):
            ret.add(child_url)

    return ret


class DownloadCommand(BaseCommand):
    name = "dl"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-n",
            "--num",
            type=int,
            default=4,
            help="number of concurrent connections",
        )

        parser.add_argument(
            "-r", "--reject", help="what urls not to download", type=re.compile
        )
        parser.add_argument(
            "-a", "--accept", help="what urls to download", type=re.compile
        )
        parser.add_argument("url", nargs="+", help="initial urls to download")

    async def run(self, args: argparse.Namespace) -> None:
        crawl_state = CrawlState(args)
        await self._initial_scan(args, crawl_state)

    async def _initial_scan(
        self, args: argparse.Namespace, crawl_state: CrawlState
    ) -> None:
        urls_to_fetch: T.Set[str] = set(args.url)

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=args.num)
        while urls_to_fetch:
            futures = [
                loop.run_in_executor(executor, _probe_url, url, crawl_state)
                for url in sorted(urls_to_fetch)
            ]
            probe_results = await asyncio.gather(
                *futures, return_exceptions=True
            )

            urls_to_fetch.clear()

            for probe_result in probe_results:
                if isinstance(probe_result, Exception):
                    continue

                if probe_result.is_media:
                    crawl_state.media_urls.add(child_url)
                    continue

                for child_url in sorted(probe_result.child_urls):
                    if child_url not in crawl_state.linkings:
                        crawl_state.linkings[child_url] = set()
                    crawl_state.linkings[child_url].add(probe_result.url)

                    if not crawl_state.args.accept.search(child_url):
                        continue
                    if (
                        crawl_state.args.reject
                        and crawl_state.args.reject.search(child_url)
                    ):
                        continue
                    if child_url in crawl_state.visited_urls:
                        continue

                    urls_to_fetch.add(child_url)

        print(crawl_state.linkings)
        print("done")
