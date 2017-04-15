#!/usr/bin/env python
import asyncio
import os
import sys
import contextlib
from pathlib import Path
from typing import Optional, List, Dict, Generator
import configargparse
from booru_toolkit import errors
from booru_toolkit import cli
from booru_toolkit import util
from booru_toolkit.plugin import PluginBase
from booru_toolkit.plugin import Post
from booru_toolkit.plugin import PluginGelbooru
from booru_toolkit.plugin import PluginPixiv
from booru_toolkit.plugin import PluginYume


PLUGINS: List[PluginBase] = [PluginGelbooru(), PluginPixiv(), PluginYume()]
MAX_ATTEMPTS = 3
MAX_CONCURRENT_DOWNLOADS = 10


class DownloadHistory:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._downloaded_urls: Dict[str, bool] = {}
        self._buffered_urls: List[str] = []
        if self._path.exists():
            for line in self._path.open('r'):
                self._downloaded_urls[line.strip()] = True

    def add(self, url: str) -> None:
        if self.is_downloaded(url):
            return
        self._downloaded_urls[url] = True
        self._buffered_urls.append(url)

    def flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open('a') as handle:
            for url in self._buffered_urls:
                print(url, file=handle)
        self._buffered_urls = []

    def is_downloaded(self, url: str) -> bool:
        return url in self._downloaded_urls


class DownloadStats:
    def __init__(self) -> None:
        self.errors = 0
        self.ignored = 0
        self.downloaded = 0

    def ignore(self, url: str, reason: str) -> None:
        print('{}: ignored ({})'.format(url, reason))
        self.ignored += 1

    @contextlib.contextmanager
    def download(self, url: str) -> Generator:
        try:
            print('{}: downloading...'.format(url))
            yield
            self.downloaded += 1
            print('{}: saved'.format(url))
        except Exception as ex:
            print('error: {}'.format(ex))
            self.errors += 1
            raise


class Downloader:
    def __init__(
            self,
            plugin: PluginBase,
            target_dir: Path,
            history: Optional[DownloadHistory],
            force: bool) -> None:
        self._plugin = plugin
        self._target_dir = target_dir
        self._history = history
        self._force = force
        self._stats = DownloadStats()

    def get_target_path(self, post: Post) -> Path:
        stem, ext = os.path.splitext(os.path.basename(post.content_url))
        if not stem.startswith(str(post.id)):
            stem = str(post.id) + '_' + stem

        file_name = (
            '_'.join(
                str(part)
                for part in [self._plugin.name, stem, post.title]
                if part)
            + '.' + ext.lstrip('.'))
        return self._target_dir.joinpath(util.sanitize_file_name(file_name))

    async def download_file(self, post: Post) -> bool:
        target_path = self.get_target_path(post)

        stem, _ = os.path.splitext(os.path.basename(post.content_url))
        history_key = '{}/{}/{}'.format(self._plugin.name, post.id, stem)

        if target_path.exists():
            self._stats.ignore(post.content_url, 'already exists')
            return False

        if (
                self._history
                and not self._force
                and self._history.is_downloaded(history_key)):
            self._stats.ignore(post.content_url, 'already downloaded')
            return False

        content = None
        attempt = 0
        with self._stats.download(post.content_url):
            while True:
                attempt += 1
                try:
                    content = await self._plugin.get_post_content(post)
                    break
                except Exception:
                    if attempt > MAX_ATTEMPTS:
                        raise

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open('wb') as handle:
            handle.write(content)

        if self._history:
            self._history.add(history_key)
            self._history.flush()

        return True

    async def run(self, query: str, limit: Optional[int]) -> None:
        downloaded = 0

        queue = asyncio.Queue(maxsize=MAX_CONCURRENT_DOWNLOADS)

        async def consumer():
            nonlocal downloaded
            while True:
                post = await queue.get()
                result = await self.download_file(post)
                if result:
                    downloaded += 1
                queue.task_done()

        consumers = [
            asyncio.ensure_future(consumer())
            for i in range(MAX_CONCURRENT_DOWNLOADS)]

        try:
            async for post in self._plugin.find_posts(query):
                if limit is not None and downloaded >= limit:
                    break
                await queue.put(post)

            # wait untli complete
            await queue.join()
        finally:
            for consumer in consumers:
                consumer.cancel()

        print('Downloaded: {}'.format(self._stats.downloaded))
        print('Ignored: {}'.format(self._stats.ignored))
        print('Errors: {}'.format(self._stats.errors))


def parse_args() -> configargparse.Namespace:
    parser = cli.make_arg_parser(
        'Downloads posts from various boorus.', PLUGINS)
    parser.add(
        '-l', '--limit', default=None, type=int,
        help='limit how many files to download')
    parser.add(
        '--target-dir', default='~/{plugin}/{query}',
        help='where to put the files')
    parser.add(
        '--history-file', default='~/.cache/dl-booru.log',
        help='path to the history file')
    parser.add(
        '-f', '--force', action='store_true',
        help='redownload even if present in the history file')
    parser.add('query', help='query to filter the posts with')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    plugin: PluginBase = args.plugin
    user_name: str = args.user
    password: str = args.password

    force: bool = args.force
    limit: Optional[int] = args.limit
    query: str = args.query

    target_dir = Path(
        args.target_dir.format(
            plugin=plugin.name,
            query=util.sanitize_file_name(query))
        ).expanduser()

    history = (
        DownloadHistory(Path(args.history_file).expanduser())
        if args.history_file
        else None)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(plugin.login(user_name, password))
        downloader = Downloader(plugin, target_dir, history, force)
        loop.run_until_complete(downloader.run(query, limit))
    except KeyboardInterrupt:
        print('Aborted.')
    except errors.ApiError as ex:
        print('Error: %s' % str(ex), file=sys.stderr)


if __name__ == '__main__':
    main()
