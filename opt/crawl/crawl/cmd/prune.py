import argparse
import concurrent.futures
import dataclasses
import typing as T
from pathlib import Path

import requests
from tqdm import tqdm

from crawl.cmd.base import BaseCommand
from crawl.flow import Flow
from crawl.history import History

# urls suffixes that can be assumed to be media files
MEDIA_EXTENSIONS = [".jpg", ".gif", ".png", ".webm"]


@dataclasses.dataclass
class PruneStats:
    total: int = 0
    removed: int = 0
    kept: int = 0
    errors: T.List[Exception] = dataclasses.field(default_factory=list)

    @property
    def skipped(self) -> int:
        return self.total - self.processed

    @property
    def processed(self) -> int:
        return self.removed + self.kept + len(self.errors)


@dataclasses.dataclass
class CheckResult:
    url: str
    is_dead: bool


def _prune(
    args: argparse.Namespace, history: History, stats: PruneStats
) -> None:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.num)

    with Flow.guard(executor):
        futures = [
            executor.submit(_check_url_is_dead, url) for url in sorted(history)
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            if future.exception():
                stats.errors.append(future.exception())
                continue
            check_result = future.result()
            if check_result.is_dead:
                history.remove(check_result.url)
                stats.removed += 1
            else:
                stats.kept += 1


def _check_url_is_dead(url: str) -> CheckResult:
    Flow.check()
    response = requests.head(url, timeout=3)
    return CheckResult(url=url, is_dead=response.status_code == 404)


class PruneCommand(BaseCommand):
    name = "prune"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-n",
            "--num",
            type=int,
            default=4,
            help="number of concurrent connections",
        )

        parser.add_argument(
            "-H",
            "--history",
            required=True,
            dest="history_path",
            metavar="FILE",
            type=Path,
            help="set path to the history file",
        )

    def run(self, args: argparse.Namespace) -> None:
        history = History()
        history.load(args.history_path)

        print("pruning...")
        try:
            stats = PruneStats(total=len(history))
            _prune(args, history, stats)
        finally:
            history.save(args.history_path)

            print("total:", stats.total)
            if stats.skipped:
                print("skipped:", stats.skipped)
            print("kept:", stats.kept)
            print("removed:", stats.removed)
            if stats.errors:
                print("errors:", len(stats.errors))
