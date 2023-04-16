from __future__ import annotations

from datetime import timedelta
import logging
import os
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
        try:
            start = default_timer()
            output = func(*args, **kwargs)
            end = default_timer()

            func_path = f"{func.__code__.co_filename.replace('.py', '')}.{func.__name__}"
            info = f"'{func_path}' took: {timedelta(seconds=end - start)}\n"
            if os.getenv("PYCHARM_HOSTED") == "1":
                # PYCHARM_HOSTED env variable equals 1 when debugging via jetbrains IDE.
                with open('time_it.txt', 'a') as f:
                    f.writelines(info)
            logging.info(info)

            return output
        except Exception as e:
            # we don't want exception in wrapper to affect real run
            logging.warning(f"[time_it] got exception: {e}")
    return wrapper
