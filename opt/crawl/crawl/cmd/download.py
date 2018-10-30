import argparse
import concurrent.futures
import dataclasses
import os
import re
import typing as T
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from crawl.cmd.base import BaseCommand
from crawl.flow import Flow
from crawl.history import History

# urls suffixes that can be assumed to be media files
MEDIA_EXTENSIONS = [".jpg", ".gif", ".png", ".webm"]


@dataclasses.dataclass
class ProbeResult:
    url: str
    is_media: bool
    child_urls: T.Set[str] = dataclasses.field(default_factory=set)


@dataclasses.dataclass
class LinkScanResult:
    errors: T.List[str] = dataclasses.field(default_factory=list)
    document_urls: T.Set[str] = dataclasses.field(default_factory=set)
    media_urls: T.Set[str] = dataclasses.field(default_factory=set)
    linkings: T.Dict[str, T.Set[str]] = dataclasses.field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.document_urls) + len(self.media_urls)


@dataclasses.dataclass
class DownloadStats:
    total: int = 0
    downloaded: int = 0
    errors: T.List[str] = dataclasses.field(default_factory=list)

    @property
    def skipped(self) -> int:
        return self.total - self.processed

    @property
    def processed(self) -> int:
        return self.downloaded + len(self.errors)


def _link_scan(args: argparse.Namespace, result: LinkScanResult) -> None:
    history = History()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.num)
    with Flow.guard(executor):
        urls_to_fetch: T.Set[str] = set(args.url)

        while urls_to_fetch:
            futures = [
                executor.submit(_probe_url, url, history)
                for url in sorted(urls_to_fetch)
                if url not in history
            ]

            urls_to_fetch.clear()

            for future in tqdm(
                concurrent.futures.as_completed(futures), total=len(futures)
            ):
                if future.exception():
                    result.errors.append(future.exception())
                    continue

                probe_result = future.result()
                if probe_result.is_media:
                    result.media_urls.add(probe_result.url)
                    continue

                result.document_urls.add(probe_result.url)
                for child_url in sorted(probe_result.child_urls):
                    if child_url not in result.linkings:
                        result.linkings[child_url] = set()
                    result.linkings[child_url].add(probe_result.url)

                    if not args.accept.search(child_url):
                        continue
                    if args.reject and args.reject.search(child_url):
                        continue

                    urls_to_fetch.add(child_url)


def _download_media(
    args: argparse.Namespace,
    link_scan_result: LinkScanResult,
    stats: DownloadStats,
) -> None:
    history = History()
    if args.history_path and args.history_path.exists():
        history.load(args.history_path)

    urls_to_fetch = sorted(set(link_scan_result.media_urls) - set(history))
    stats.total = len(urls_to_fetch)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.num)
    try:
        with Flow.guard(executor):
            futures = [
                executor.submit(
                    _download_url, url, history, args, link_scan_result
                )
                for url in urls_to_fetch
            ]

            for future in tqdm(
                concurrent.futures.as_completed(futures), total=len(futures)
            ):
                if future.exception():
                    stats.errors.append(future.exception())
                else:
                    stats.downloaded += 1
    finally:
        if args.history_path:
            history.save(args.history_path)


def _probe_url(url: str, history: History) -> ProbeResult:
    Flow.check()

    history.add(url)

    if not url.endswith(tuple(MEDIA_EXTENSIONS)):
        response = requests.head(url, timeout=3)
        response.raise_for_status()

        mime = response.headers["content-type"].split(";")[0].lower()
        if mime == "text/html":
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            return ProbeResult(
                url=url, is_media=False, child_urls=_collect_links(response)
            )

    return ProbeResult(url=url, is_media=True)


def _download_url(
    url: str,
    history: History,
    args: argparse.Namespace,
    link_scan_result: LinkScanResult,
) -> Path:
    Flow.check()
    target_path = _get_target_path(url, args, link_scan_result)

    if not target_path.exists():
        response = requests.get(url, timeout=3)
        response.raise_for_status()

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(response.content)
        history.add(url)

    return target_path


def _get_target_path(
    url: str, args: argparse.Namespace, link_scan_result: LinkScanResult
) -> Path:
    parsed_url = urllib.parse.urlparse(url)

    if args.parent and url in link_scan_result.linkings:
        for parent_url in link_scan_result.linkings[url]:
            if args.parent.search(parent_url):
                parsed_parent_url = urllib.parse.urlparse(parent_url)
                return (
                    args.target_dir
                    / parsed_parent_url.netloc
                    / re.sub(r"^[\/]*", "", parsed_parent_url.path)
                    / os.path.basename(parsed_url.path)
                )

    return (
        args.target_dir
        / parsed_url.netloc
        / re.sub(r"^[\/]*", "", parsed_url.path)
    )


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
            dest="target_dir",
            metavar="DIR",
            default=".",
            type=Path,
            help="set base target directory",
        )
        parser.add_argument(
            "-H",
            "--history",
            dest="history_path",
            metavar="FILE",
            type=Path,
            help="set path to the history file",
        )
        parser.add_argument(
            "-r", "--reject", type=re.compile, help="what urls not to download"
        )
        parser.add_argument(
            "-a", "--accept", type=re.compile, help="what urls to download"
        )
        parser.add_argument(
            "-p",
            "--parent",
            type=re.compile,
            help=(
                "reparents downloaded files to "
                "a source url that matches this regex"
            ),
        )
        parser.add_argument("url", nargs="+", help="initial urls to download")

    def run(self, args: argparse.Namespace) -> None:
        print("scanning for links...")
        try:
            link_scan_result = LinkScanResult()
            _link_scan(args, link_scan_result)
        finally:
            print("total:", link_scan_result.total)
            print("documents:", len(link_scan_result.document_urls))
            print("media:", len(link_scan_result.media_urls))
            if link_scan_result.errors:
                print("errors:", len(link_scan_result.errors))

        print("downloading media...")
        try:
            stats = DownloadStats()
            _download_media(args, link_scan_result, stats)
        finally:
            print("total:", stats.total)
            if stats.skipped:
                print("skipped:", stats.skipped)
            print("downloaded:", stats.downloaded)
            if stats.errors:
                print("errors:", len(stats.errors))
                for error in stats.errors:
                    print(error)
