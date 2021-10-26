import concurrent.futures
import multiprocessing
import os
import platform
from collections import Callable
from typing import Any, List, Generator, Iterator


class ParallelFunctionRunner:
    def __init__(self, workers_number=None):
        self.workers_number = workers_number if workers_number else os.cpu_count()
        self.os = platform.system()

    def run_func_parallel(self, func: Callable[..., Any], data: List[Any]) -> Iterator:
        if self.os == 'Windows':
            return self._run_function_multithreaded(func, data)
        else:
            return self._run_function_multiprocess(func, data)

    def _run_function_multiprocess(self, func: Callable[..., Any], data: List[Any]) -> Generator[Any, None, None]:
        group_size = int(len(data) / self.workers_number) + 1
        groups_of_data = [data[i: i + group_size] for i in range(0, len(data), group_size)]

        def func_wrapper(original_func, data_group, connection):
            for item in data_group:
                result = original_func(item)
                connection.send(result)
            connection.close()

        processes = []
        for group_of_data in groups_of_data:
            parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
            process = multiprocessing.get_context("fork").Process(target=func_wrapper,
                                                                  args=(func, group_of_data, child_conn))
            processes.append((process, parent_conn, len(group_of_data)))
            process.start()

        for process, parent_conn, group_len in processes:
            for i in range(group_len):
                yield parent_conn.recv()

    def _run_function_multithreaded(self, func: Callable[..., Any], data: List[Any]) -> Iterator:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            return executor.map(func, data)


parallel_function_runner = ParallelFunctionRunner()
