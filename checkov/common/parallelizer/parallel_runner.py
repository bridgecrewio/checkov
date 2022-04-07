# flake8: noqa: E741

from __future__ import annotations

import concurrent.futures
import multiprocessing
import os
import platform
from collections.abc import Iterator, Iterable
from multiprocessing.pool import Pool
from typing import Generator, Callable, TypeVar, TYPE_CHECKING

from checkov.common.models.enums import ParallelizationType

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

I = TypeVar("I")
O = TypeVar("O")


class ParallelRunner:
    def __init__(self, workers_number: int | None = None) -> None:
        self.workers_number = workers_number if workers_number else (os.cpu_count() or 1)
        self.os = platform.system()
        self.type = os.getenv("CHECKOV_PARALLELIZATION_TYPE", ParallelizationType.SPAWN)

    def run_function(self, func: Callable[[I], O], items: list[I], group_size: int | None = None) -> Iterable[O]:
        if self.type == ParallelizationType.FORK:
            return self._run_function_multiprocess_fork(func, items, group_size)
        elif self.type == ParallelizationType.SPAWN:
            return self._run_function_multiprocess_spawn(func, items)
        elif self.type == ParallelizationType.THREAD:
            return self._run_function_multithreaded(func, items)
        else:
            # no parallelization, just create a generator
            return (func(item) for item in items)

    def _run_function_multiprocess_fork(
        self, func: Callable[[I], O], items: list[I], group_size: int | None
    ) -> Generator[O, None, None]:
        if not group_size:
            group_size = int(len(items) / self.workers_number) + 1
        groups_of_items = [items[i : i + group_size] for i in range(0, len(items), group_size)]

        def func_wrapper(original_func: Callable[[I], O], items_group: list[I], connection: Connection) -> None:
            for item in items_group:
                result = original_func(item)
                connection.send(result)
            connection.close()

        processes = []
        for group_of_items in groups_of_items:
            parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
            process = multiprocessing.get_context("fork").Process(
                target=func_wrapper, args=(func, group_of_items, child_conn)
            )
            processes.append((process, parent_conn, len(group_of_items)))
            process.start()

        for process, parent_conn, group_len in processes:
            for _ in range(group_len):
                try:
                    yield parent_conn.recv()
                except EOFError:
                    pass

    def _run_function_multiprocess_spawn(self, func: Callable[[I], O], items: list[I]) -> list[O]:
        with Pool(processes=1, context=multiprocessing.get_context("spawn")) as p:
            chunksize = int(len(items) / self.workers_number) + 1
            return p.map(func, items, chunksize=chunksize)

    def _run_function_multithreaded(self, func: Callable[[I], O], items: list[I]) -> Iterator[O]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            return executor.map(func, items)


parallel_runner = ParallelRunner()
