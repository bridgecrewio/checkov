import concurrent
import hashlib
import json
import os
from typing import Union, List, Dict, Any, Callable, Optional
import concurrent.futures
from multiprocessing import Process, Pipe


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


def print_edge(e):
    print(e)


def run_function_multiprocessed(
        func: Callable[..., Any], data: List[List[Any]], max_group_size: int, num_of_workers: Optional[int] = None
) -> List[Any]:
    def thread_wrapper(arg, conn):
        result = func(arg)
        conn.send([result])
        conn.close()

    groups_of_data = [data[i: i + max_group_size] for i in range(0, len(data), max_group_size)]
    # if not num_of_workers:
    num_of_workers = min(len(groups_of_data), 1024, int(os.cpu_count()/2))
    print(f"running in parallel with {num_of_workers} processes and {len(groups_of_data)} groups_of_data")

    results = []
    iteration = 0
    while iteration * num_of_workers < len(groups_of_data):
        # print(f"iteration {iteration}")
        curr_data = groups_of_data[iteration * num_of_workers:(iteration * num_of_workers) + num_of_workers]
        # if iteration == 681:
        #     print(curr_data)
        processes = []
        parent_connections = []
        for i in range(min(num_of_workers, len(curr_data))):
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)

            if iteration == 681:
                print(f"curr_data[{i}] = {curr_data[i][0][0]}")
            # create the process, pass instance and connection
            process = Process(target=thread_wrapper, args=(curr_data[i], child_conn,))
            processes.append(process)

        for process in processes:
            process.start()
        # if iteration >= 680:
        #     print("Started!")

        for process in processes:
            # if iteration >= 680:
            #     print("joinnnnn")
            process.join(5)

        for parent_connection in parent_connections:
            # if iteration >= 680:
            #     print("receiving...")
            res = parent_connection.recv()
            # if iteration >= 680:
            #     print("DONE receiving...")
            if res:
                results.append(res[0])

        iteration += 1
    return results

# def run_function_multiprocessed(
#     func: Callable[..., Any], data: List[List[Any]], max_group_size: int, num_of_workers: Optional[int] = None
# ) -> None:
#     groups_of_data = [data[i : i + max_group_size] for i in range(0, len(data), max_group_size)]
#     flattened_data = [item for sublist in data for item in sublist]
#     if not num_of_workers:
#         num_of_workers = len(groups_of_data)
#     if num_of_workers > 0:
#         with Pool(num_of_workers) as pool:
#             pool.map(func, flattened_data)
#             # futures = {executor.submit(func, data_group): data_group for data_group in groups_of_data}
#             # wait_result = concurrent.futures.wait(futures)
#             # if wait_result.not_done:
#             #     raise Exception(f"failed to perform {func.__name__}")
#             # for future in futures:
#             #     try:
#             #         future.result()
#             #     except Exception as e:
#             #         raise e
