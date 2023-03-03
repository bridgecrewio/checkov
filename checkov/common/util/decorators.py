from __future__ import annotations

from datetime import timedelta
import logging
from functools import wraps
from timeit import default_timer
from typing import TypeVar, Callable

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


def time_it(func: Callable[P, T]) -> Callable[P, T]:
    """Prints the time it took to execute the function"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = default_timer()
        output = func(*args, **kwargs)
        end = default_timer()

        func_path = f"{func.__code__.co_filename.replace('.py', '')}.{func.__name__}"
        logging.info(f"'{func_path}' took: {timedelta(seconds=end - start)}")

        return output
    return wrapper
