from __future__ import annotations

import concurrent
import hashlib
from typing import Any, Callable, overload, Union, List, Dict
import concurrent.futures

from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import force_int


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


def to_list(data: Any) -> list[Any] | dict[str, Any]:
    if isinstance(data, list) and len(data) == 1 and (isinstance(data[0], str) or isinstance(data[0], int)):
        return data
    elif isinstance(data, list):
        return [to_list(x) for x in data]
    elif isinstance(data, dict):
        return {key: to_list(val) for key, val in data.items()}
    else:
        return [data]


@overload
def update_dictionary_attribute(
        config: dict[str, Any], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> dict[str, Any]:
    ...


@overload
def update_dictionary_attribute(
        config: list[Any], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> list[Any]:
    ...


def update_dictionary_attribute(
    config: Union[List[Any], Dict[str, Any]], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> Union[List[Any], Dict[str, Any]]:
    key_parts = key_to_update.split(".")
    if '"' in key_to_update:
        key_parts = join_double_quote_surrounded_dot_split(str_parts=key_parts)

    if isinstance(config, dict) and isinstance(key_parts, list):
        key = key_parts[0]
        inner_config = config.get(key)

        if inner_config is not None:
            if len(key_parts) == 1:
                if isinstance(inner_config, list) and not isinstance(new_value, list):
                    new_value = [new_value]
                config[key] = to_list(new_value) if dynamic_blocks else new_value
                return config
            else:
                config[key] = update_dictionary_attribute(
                    inner_config, ".".join(key_parts[1:]), new_value, dynamic_blocks=dynamic_blocks
                )
        else:
            for key in config:
                config[key] = update_dictionary_attribute(
                    config[key], key_to_update, new_value, dynamic_blocks=dynamic_blocks
                )
    if isinstance(config, list):
        return update_list_attribute(
            config=config,
            key_parts=key_parts,
            key_to_update=key_to_update,
            new_value=new_value,
            dynamic_blocks=dynamic_blocks,
        )
    return config


def update_list_attribute(
    config: list[Any], key_parts: list[str], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> list[Any] | dict[str, Any]:
    """Updates a list attribute in the given config"""

    if not config:
        # happens when we can't correctly evaluate something, because of strange defaults or 'for_each' blocks
        return config

    if len(key_parts) == 1 and len(config) == 1:
        idx = force_int(key_parts[0])
        # Avoid changing the config and cause side effects
        inner_config = pickle_deepcopy(config[0])

        if idx is not None and isinstance(inner_config, list):
            if not inner_config:
                # happens when config = [[]]
                return config

            inner_config[idx] = new_value
            return [inner_config]
    entry_to_update = int(key_parts[0]) if key_parts[0].isnumeric() else -1
    for i, config_value in enumerate(config):
        if entry_to_update == -1:
            config[i] = update_dictionary_attribute(config=config_value, key_to_update=key_to_update, new_value=new_value, dynamic_blocks=dynamic_blocks)
        elif entry_to_update == i:
            config[i] = update_dictionary_attribute(config=config_value, key_to_update=".".join(key_parts[1:]), new_value=new_value, dynamic_blocks=dynamic_blocks)

    return config


def join_double_quote_surrounded_dot_split(str_parts: list[str]) -> list[str]:
    """Joins back split strings which enclosed a dot by double quotes

    ex.

    ['google_project_iam_binding', 'role["roles/logging', 'admin"]'] -> ['google_project_iam_binding', 'role["roles/logging.admin"]']

    If someone finds a better solution feel free to replace it!
    """

    new_str_parts = []
    joined_str_parts: list[str] = []
    for part in str_parts:
        if not joined_str_parts:
            if '"' not in part:
                new_str_parts.append(part)
            elif part.count('"') >= 2:
                new_str_parts.append(part)
            else:
                joined_str_parts.append(part)
            continue

        joined_str_parts.append(part)

        if '"' in part:
            new_str_parts.append(".".join(joined_str_parts))
            joined_str_parts = []

    return new_str_parts
