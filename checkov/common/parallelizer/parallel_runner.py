from __future__ import annotations

import concurrent.futures
import logging
import multiprocessing
import os
import platform
from collections.abc import Iterator, Iterable
from multiprocessing.pool import Pool
from typing import Any, List, Generator, Callable, Optional, TypeVar, TYPE_CHECKING

from checkov.common.models.enums import ParallelizationType

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

_T = TypeVar("_T")


class ParallelRunException(Exception):
    def __init__(self, internal_exception: Exception) -> None:
        self.internal_exception = internal_exception
        super().__init__(internal_exception)


class ParallelRunner:
    def __init__(
        self, workers_number: int | None = None,
        parallelization_type: ParallelizationType = ParallelizationType.FORK
    ) -> None:
        self.workers_number = (workers_number if workers_number else os.cpu_count()) or 1
        self.os = platform.system()
        self.type: str | ParallelizationType = parallelization_type
        custom_type = os.getenv("CHECKOV_PARALLELIZATION_TYPE")
        if custom_type:
            self.type = custom_type
        elif os.getenv("PYCHARM_HOSTED") == "1":
            # PYCHARM_HOSTED env variable equals 1 when debugging via jetbrains IDE.
            # To prevent JetBrains IDE from crashing on debug run sequentially
            self.type = ParallelizationType.NONE
        elif self.os == "Windows" or self.os == "Darwin":
            if self.type in [ParallelizationType.FORK, ParallelizationType.SPAWN]:
                # 'fork' mode is not supported on 'Windows', and has security issues on macOS
                # 'spawn' mode currently is not supported due to its memory erasure for each new process, which conflicts with the child processes' need for the parent's memory."
                self.type = ParallelizationType.THREAD
        # future support - spawn is not working well with frozen mode, need to investigate multiprocessing.freeze_support()

    def running_as_process(self) -> bool:
        return self.type in [ParallelizationType.FORK, ParallelizationType.SPAWN]

    def run_function(
        self,
        func: Callable[..., _T],
        items: List[Any],
        group_size: Optional[int] = None,
    ) -> Iterable[_T]:
        if self.type == ParallelizationType.THREAD:
            return self._run_function_multithreaded(func, items)
        elif self.type == ParallelizationType.FORK:
            return self._run_function_multiprocess_fork(func, items, group_size)
        elif self.type == ParallelizationType.SPAWN:
            return self._run_function_multiprocess_spawn(func, items, group_size)
        else:
            return self._run_function_sequential(func, items)

    def _run_function_multiprocess_fork(
        self, func: Callable[[Any], _T], items: List[Any], group_size: Optional[int]
    ) -> Generator[_T, None, None]:
        if not group_size:
            group_size = int(len(items) / self.workers_number) + 1
        groups_of_items = [items[i: i + group_size] for i in range(0, len(items), group_size)]

        def func_wrapper(original_func: Callable[[Any], _T], items_group: List[Any], connection: Connection) -> None:
            for item in items_group:
                try:
                    if isinstance(item, tuple):
                        # unpack a tuple to pass multiple arguments to the target function
                        result = original_func(*item)
                    else:
                        result = original_func(item)

                    connection.send(result)
                except Exception as e:
                    logging.error(
                        f"Failed to invoke function {func.__code__.co_filename.replace('.py', '')}.{func.__name__} with {item}",
                        exc_info=True,
                    )
                    connection.send(ParallelRunException(e))

            connection.close()

        logging.debug(
            f"Running function {func.__code__.co_filename.replace('.py', '')}.{func.__name__} with parallelization type 'fork'"
        )
        processes = []
        for group_of_items in groups_of_items:
            parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
            process = multiprocessing.get_context("fork").Process(
                target=func_wrapper, args=(func, group_of_items, child_conn)
            )
            processes.append((process, parent_conn, len(group_of_items)))
            process.start()

        for _, parent_conn, group_len in processes:
            for _ in range(group_len):
                try:
                    v = parent_conn.recv()

                    if isinstance(v, ParallelRunException):
                        raise v.internal_exception.with_traceback(v.internal_exception.__traceback__)

                    yield v
                except EOFError:
                    pass

    def _run_function_multiprocess_spawn(
        self, func: Callable[[Any], _T], items: list[Any], group_size: int | None
    ) -> Iterable[_T]:
        if multiprocessing.current_process().daemon:
            # can't create a new pool, when already inside a pool
            return self._run_function_multithreaded(func, items)

        if not group_size:
            group_size = int(len(items) / self.workers_number) + 1

        logging.debug(
            f"Running function {func.__code__.co_filename.replace('.py', '')}.{func.__name__} with parallelization type 'spawn'"
        )
        with Pool(processes=self.workers_number, context=multiprocessing.get_context("spawn")) as p:
            if items and isinstance(items[0], tuple):
                # need to use 'starmap' to pass multiple arguments to the target function
                return p.starmap(func, items, chunksize=group_size)

            return p.map(func, items, chunksize=group_size)

    def _run_function_multithreaded(self, func: Callable[[Any], _T], items: List[Any]) -> Iterator[_T]:
        logging.debug(
            f"Running function {func.__code__.co_filename.replace('.py', '')}.{func.__name__} with parallelization type 'thread'"
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            if items and isinstance(items[0], tuple):
                # split a list of tuple into tuples of the positioned values of the tuple
                return executor.map(func, *list(
                    zip(*items)))  # noqa[B905]  # no need to set 'strict' otherwise 'mypy' complains

            return executor.map(func, items)

    def _run_function_sequential(self, func: Callable[[Any], _T], items: List[Any]) -> Iterator[_T]:
        logging.debug(
            f"Running function {func.__code__.co_filename.replace('.py', '')}.{func.__name__} with parallelization type 'none'"
        )
        if items and isinstance(items[0], tuple):
            # unpack a tuple to pass multiple arguments to the target function
            return (func(*item) for item in items)

        return (func(item) for item in items)


parallel_runner = ParallelRunner()
