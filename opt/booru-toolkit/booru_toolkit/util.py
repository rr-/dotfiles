import asyncio
import functools
import re
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar

TResult = Any
TCallable = Callable[..., TResult]


def sanitize_file_name(name: str) -> str:
    return re.sub(r'[\\\/:*?"<>|]', "_", name)


# credit: http://stackoverflow.com/a/39628789
def async_lru_cache(maxsize: int = 128) -> TCallable:
    cache = OrderedDict()
    awaiting: dict[Any, TResult] = dict()

    async def run_and_cache(
        func: TCallable, args: Any, kwargs: Any
    ) -> TResult:
        result = await func(*args, **kwargs)
        key = functools._make_key(args, kwargs, False)
        cache[key] = result
        if len(cache) > maxsize:
            cache.popitem(False)
        cache.move_to_end(key)
        return result

    def decorator(func: TCallable) -> TCallable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> TResult:
            key = functools._make_key(args, kwargs, False)
            if key in cache:
                return cache[key]
            if key in awaiting:
                task = awaiting[key]
                return await asyncio.wait_for(task, timeout=None)
            task = asyncio.ensure_future(run_and_cache(func, args, kwargs))
            awaiting[key] = task
            result = await asyncio.wait_for(task, timeout=None)
            del awaiting[key]
            return result

        return wrapper

    return decorator


def clamp(number: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, number))


async def retry(
    max_attempts: int,
    sleep: float,
    func: Callable[..., TResult],
    *args: Any,
    **kwargs: Any
) -> TResult:
    attempt = 0
    while True:
        attempt += 1
        try:
            result = await func(*args, **kwargs)
            await asyncio.sleep(sleep)
            break
        except Exception:
            if attempt > max_attempts:
                raise
    return result
