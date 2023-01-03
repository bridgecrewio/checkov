import logging
import time
from functools import wraps
from typing import Any


def timeit(func: Any) -> Any:
    @wraps(func)
    def timeit_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper
