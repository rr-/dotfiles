import concurrent.futures
import contextlib
from typing import Iterator


class Flow:
    shutdown = False

    @staticmethod
    @contextlib.contextmanager
    def guard(executor: concurrent.futures.Executor) -> Iterator[None]:
        try:
            yield
        except KeyboardInterrupt:
            Flow.shutdown = True
            executor.shutdown(wait=False)
            raise InterruptedError

    @staticmethod
    def check() -> None:
        if Flow.shutdown:
            raise InterruptedError
