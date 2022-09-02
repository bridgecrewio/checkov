from __future__ import annotations

import concurrent.futures
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
            -> Generator[Any, None, None]:
        if not group_size:
            group_size = int(len(items) / self.workers_number) + 1
        groups_of_items = [items[i: i + group_size] for i in range(0, len(items), group_size)]

        def func_wrapper(original_func: Callable[[Any], Any], items_group: List[Any], connection: Connection) -> None:
            for item in items_group:
                result = original_func(item)
                connection.send(result)
            connection.close()

        processes = []
        for group_of_items in groups_of_items:
            parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
            process = multiprocessing.get_context("fork").Process(target=func_wrapper,
                                                                  args=(func, group_of_items, child_conn))
            processes.append((process, parent_conn, len(group_of_items)))
            process.start()

        for _, parent_conn, group_len in processes:
            for _ in range(group_len):
                try:
                    yield parent_conn.recv()
                except EOFError:
                    pass

    def _run_function_multithreaded(self, func: Callable[[Any], _T], items: List[Any]) -> Iterator[_T]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            return executor.map(func, items)


parallel_runner = ParallelRunner()
