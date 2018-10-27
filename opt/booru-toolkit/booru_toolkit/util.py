import re
import asyncio
import functools
from collections import OrderedDict
from typing import Any, Dict


class bidict(dict):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.inverse: Dict = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key: Any) -> None:
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)


def sanitize_file_name(name: str) -> str:
    return re.sub(r'[\\\/:*?"<>|]', "_", name)


# credit: http://stackoverflow.com/a/39628789
def async_lru_cache(maxsize=128):
    cache = OrderedDict()
    awaiting = dict()

    async def run_and_cache(func, args, kwargs):
        result = await func(*args, **kwargs)
        key = functools._make_key(args, kwargs, False)
        cache[key] = result
        if len(cache) > maxsize:
            cache.popitem(False)
        cache.move_to_end(key)
        return result

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
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


async def retry(max_attempts, sleep, func, *args, **kwargs):
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
