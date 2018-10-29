import argparse
import concurrent.futures
import dataclasses
import re
import typing as T
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from crawl.cmd.base import BaseCommand

# urls suffixes that can be assumed to be media files
MEDIA_EXTENSIONS = [".jpg", ".gif", ".png", ".webm"]


@dataclasses.dataclass
class ProbeResult:
    url: str
    is_media: bool
    child_urls: T.Set[str] = dataclasses.field(default_factory=set)


class Crawler:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

        self.media_urls: T.Set[str] = set()
        self.linkings: T.Dict[str, T.Set[str]] = {}

        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=args.num
        )

    # phase 1
    # modifies media_urls and linkings
    def initial_scan(self) -> None:
        visited_urls: T.Set[str] = set()
        urls_to_fetch: T.Set[str] = set(self.args.url)
        while urls_to_fetch:
            urls_to_fetch = set(
                self._probe_batch_urls(urls_to_fetch, visited_urls)
            )

    # phase 2
    def download_media(self) -> int:
        visited_urls = set()
        futures = [
            self.executor.submit(self._download_url, url, visited_urls)
            for url in sorted(self.media_urls)
            if url not in visited_urls
        ]
        downloaded = 0
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            if future.exception():
                print(future.exception())
            else:
                downloaded += 1
        return downloaded

    def _probe_batch_urls(
        self, urls: T.Iterable[str], visited_urls: T.Set[str]
    ) -> T.Iterable[str]:
        futures = [
            self.executor.submit(self._probe_url, url, visited_urls)
            for url in sorted(urls)
            if url not in visited_urls
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            if future.exception():
                continue
            probe_result = future.result()
            yield from self._process_probe_result(probe_result)

    def _probe_url(self, url: str, visited_urls: T.Set[str]) -> ProbeResult:
        visited_urls.add(url)

        if not url.endswith(tuple(MEDIA_EXTENSIONS)):
            response = requests.head(url, timeout=3)
            response.raise_for_status()

            mime = response.headers["content-type"].split(";")[0].lower()
            if mime == "text/html":
                response = requests.get(url, timeout=3)
                response.raise_for_status()
                return ProbeResult(
                    url=url,
                    is_media=False,
                    child_urls=_collect_links(response),
                )

        return ProbeResult(url=url, is_media=True)

    def _process_probe_result(
        self, probe_result: ProbeResult
    ) -> T.Iterable[str]:
        if probe_result.is_media:
            self.media_urls.add(probe_result.url)
        else:
            for child_url in sorted(probe_result.child_urls):
                if child_url not in self.linkings:
                    self.linkings[child_url] = set()
                self.linkings[child_url].add(probe_result.url)

                if self._can_visit(child_url):
                    yield child_url

    def _download_url(self, url: str, visited_urls: T.Set[str]) -> Path:
        parsed_url = urllib.parse.urlparse(url)
        target_path = (
            self.args.target /
            parsed_url.netloc /
            re.sub(r"^[\/]*", "", parsed_url.path)
        )
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if not target_path.exists():
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            target_path.write_bytes(response.content)
            visited_urls.add(url)

        return target_path

    def _can_visit(self, url: str) -> bool:
        if not self.args.accept.search(url):
            return False
        if self.args.reject and self.args.reject.search(url):
            return False
        return True


def _collect_links(response: requests.Response) -> T.Set[str]:
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
            "-t",
            "--target",
            metavar="DIR",
            default=".",
            type=Path,
            help="set base target directory",
        )
        parser.add_argument(
            "-r", "--reject", help="what urls not to download", type=re.compile
        )
        parser.add_argument(
            "-a", "--accept", help="what urls to download", type=re.compile
        )
        parser.add_argument("url", nargs="+", help="initial urls to download")

    def run(self, args: argparse.Namespace) -> None:
        crawler = Crawler(args)

        print("initial html scan")
        crawler.initial_scan()

        print("media download")
        downloaded = crawler.download_media()
        print("downloaded", downloaded, "media files")
