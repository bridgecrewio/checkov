from __future__ import annotations

import concurrent.futures
import logging
import multiprocessing
import os
import platform
from typing import Any, List, Generator, Iterator, Callable, Optional, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

_T = TypeVar("_T")


class ParallelRunner:
    def __init__(self, workers_number: int | None = None) -> None:
        self.workers_number = (workers_number if workers_number else os.cpu_count()) or 1
        self.os = platform.system()

    def run_function(self, func: Callable[[Any], _T], items: List[Any], group_size: Optional[int] = None, run_multiprocess: Optional[bool] = False) -> Iterator[_T]:
        if self.os == 'Windows' or (not run_multiprocess and os.getenv("PYCHARM_HOSTED") == "1"):
            # PYCHARM_HOSTED env variable equals 1 when debugging via jetbrains IDE.
            # To prevent JetBrains IDE from crashing on debug use multi threading
            # Override this condition if run_multiprocess is set to True
            return self._run_function_multithreaded(func, items)
        else:
            return self._run_function_multiprocess(func, items, group_size)

    def _run_function_multiprocess(self, func: Callable[[Any], Any], items: List[Any], group_size: Optional[int]) \
            -> Iterator[_T]:
        logging.info(f"[_run_function_multiprocess] starting with {self.workers_number} workers")
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.workers_number) as executor:
            return executor.map(func, items)

    def _run_function_multithreaded(self, func: Callable[[Any], _T], items: List[Any]) -> Iterator[_T]:
        logging.info(f"[_run_function_multithreaded] starting with {self.workers_number} workers")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            return executor.map(func, items)


parallel_runner = ParallelRunner()
