import concurrent.futures
import contextlib
import typing as T


class Flow:
    shutdown = False

    @staticmethod
    @contextlib.contextmanager
    def guard(executor: concurrent.futures.Executor) -> T.Generator:
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
