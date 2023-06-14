from __future__ import annotations

import os
import pickle  # nosec  # only own data is pickled
import shelve  # nosec  # only own data is pickled
import time
from functools import wraps
from typing import TypeVar, Callable, Any, cast

from typing_extensions import ParamSpec

from checkov.common.util.env_vars_config import env_vars_config

T = TypeVar("T")
P = ParamSpec("P")


def ttl_cached(seconds: int, key: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Caches the returned object for the given seconds"""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            output = cast("T | None", file_cache.get_ttl_item(key=key))
            if output is not None:
                return output

            output = func(*args, **kwargs)

            if output is not None:
                file_cache.set_ttl_item(ttl=seconds, key=key, value=output)

            return output

        return wrapper

    return decorator


class FileCache:
    """Singleton to create and interact with a local file cache"""

    def __init__(self) -> None:
        self.enabled = False  # can be enabled anytime

        self._ttl_shelf: shelve.Shelf[Any] | None = None
        self._ttl_shelf_filename = os.path.join(env_vars_config.CACHE_DIR, "ttl_cache")

    def init_cache(self) -> None:
        # needs to be done separately, if someone decides not to use caching
        if self._ttl_shelf is None:
            os.makedirs(env_vars_config.CACHE_DIR, exist_ok=True)
            self._ttl_shelf = shelve.open(self._ttl_shelf_filename, protocol=pickle.HIGHEST_PROTOCOL, flag="c")  # nosec  # only own data is pickled

    def get_ttl_item(self, key: str) -> Any:
        if not self.enabled or self._ttl_shelf is None:
            return None

        ttl_value = self._ttl_shelf.get(key)
        if ttl_value is not None:
            # check, if it maybe expired
            if ttl_value[0] > int(time.time()):
                return ttl_value[1]

            del self._ttl_shelf[key]

        return None

    def set_ttl_item(self, ttl: int, key: str, value: Any) -> None:
        if not self.enabled or self._ttl_shelf is None:
            return

        expires = int(time.time()) + ttl
        self._ttl_shelf[key] = (expires, value)
        self._ttl_shelf.sync()


file_cache = FileCache()
