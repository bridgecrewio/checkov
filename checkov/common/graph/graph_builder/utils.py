import concurrent
import hashlib
import json
from typing import Union, List, Dict, Any, Callable, Optional


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
