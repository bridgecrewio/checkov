from __future__ import annotations

import concurrent
import hashlib
from typing import Any, Callable
import concurrent.futures


def calculate_hash(data: Any) -> str:
    sha256 = hashlib.sha256(str(data).encode("utf-8"))
    return sha256.hexdigest()


def join_trimmed_strings(char_to_join: str, str_lst: list[str], num_to_trim: int) -> str:
    return char_to_join.join(str_lst[: len(str_lst) - num_to_trim])


def run_function_multithreaded(
    func: Callable[..., Any], data: list[list[Any]], max_group_size: int, num_of_workers: int | None = None
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
                except Exception:
                    raise


def filter_sub_keys(key_list: list[str]) -> list[str]:
    filtered_key_list = []
    for key in key_list:
        if not any(other_key != key and other_key.startswith(key) for other_key in key_list) and is_include_dup_dynamic(key, key_list):
            filtered_key_list.append(key)
    return filtered_key_list


def is_include_dup_dynamic(key: str, list_keys: list[str]) -> bool:
    return f"dynamic.{key.split('.')[0]}" not in list_keys


def adjust_value(element_name: str, value: Any) -> Any:
    """Adjusts the value, if the 'element_name' references a nested key

    Ex:
    element_name = publicKey.keyData
    value = {"keyData": "key-data", "path": "path"}

    returns new_value = "key-data"
    """

    if "." in element_name and isinstance(value, dict):
        key_parts = element_name.split(".")
        new_value = value.get(key_parts[1])

        if new_value is None:
            # couldn't find key in in value object
            return None

        return adjust_value(".".join(key_parts[1:]), new_value)

    return value
