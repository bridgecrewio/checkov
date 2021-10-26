import concurrent
import hashlib
import json
import multiprocessing
import os
from multiprocessing import Pipe
from typing import Union, List, Dict, Any, Callable, Optional, Generator
import concurrent.futures



def stringify_value(value: Union[bool, int, float, str, List[str], Dict[str, Any]]) -> str:
    if isinstance(value, bool):
        value = str(value).lower()
    elif isinstance(value, (float, int)):
        value = str(value)
    return json.dumps(value, indent=4, default=str)


def calculate_hash(data: Union[bool, int, float, str, Dict[str, Any]]) -> str:
    encoded_attributes = stringify_value(data)
    sha256 = hashlib.sha256()
    sha256.update(repr(encoded_attributes).encode("utf-8"))

    return sha256.hexdigest()


def join_trimmed_strings(char_to_join: str, str_lst: List[str], num_to_trim: int) -> str:
    return char_to_join.join(str_lst[: len(str_lst) - num_to_trim])


def run_function_multithreaded(
    func: Callable[..., Any], data: List[List[Any]], max_group_size: int, num_of_workers: Optional[int] = None
) -> None:
    groups_of_data = [data[i : i + max_group_size] for i in range(0, len(data), max_group_size)]
    if not num_of_workers:
        num_of_workers = len(groups_of_data)
    if num_of_workers > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
            futures = {executor.submit(func, data_group): data_group for data_group in groups_of_data}
            wait_result = concurrent.futures.wait(futures)
            if wait_result.not_done:
                raise Exception(f"failed to perform {func.__name__}")
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    raise e


def run_function_multiprocess(
    func: Callable[..., Any], data: List[Any], num_of_workers: Optional[int] = None) -> Generator[Any, None, None]:
    if not num_of_workers:
        num_of_workers = os.cpu_count()
    max_group_size = int(len(data) / num_of_workers) + 1
    groups_of_data = [data[i: i + max_group_size] for i in range(0, len(data), max_group_size)]

    def func_wrapper(original_func, data_group, connection):
        for item in data_group:
            result = original_func(item)
            connection.send(result)
        connection.close()

    processes = []
    for group_of_data in groups_of_data:
        parent_conn, child_conn = Pipe(duplex=False)
        process = multiprocessing.get_context("fork").Process(target=func_wrapper,
                                                              args=(func, group_of_data, child_conn))
        processes.append((process, parent_conn, len(group_of_data)))
        process.start()

    for process, parent_conn, group_len in processes:
        for i in range(group_len):
            yield parent_conn.recv()
