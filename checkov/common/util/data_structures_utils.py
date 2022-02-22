import logging
from typing import Generator, Any, Union, Dict


def get_inner_dict(source_dict, path_as_list):
    result = source_dict
    for index in path_as_list:
        result = result[index]
    return result


def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two or more dicts. If there are duplicate keys, later dict arguments take precedence.

    Null, empty, or non-dict arguments are qiuetly skipped.
    :param dicts:
    :return:
    """
    res: Dict[Any, Any] = {}
    for d in dicts:
        if not d or not isinstance(d, dict):
            continue
        res = {**res, **d}
    return res


def generator_reader_wrapper(g: Generator) -> Union[None, Any]:
    try:
        return next(g)
    except StopIteration:
        return


def search_deep_keys(search_text, obj, path):
    """Search deep for keys and get their values"""
    keys = []
    if isinstance(obj, dict):
        for key in obj:
            pathprop = path[:]
            pathprop.append(key)
            if key == search_text:
                pathprop.append(obj[key])
                keys.append(pathprop)
                # pop the last element off for nesting of found elements for
                # dict and list checks
                pathprop = pathprop[:-1]
            if isinstance(obj[key], dict):
                if key != 'parent_metadata':
                    # Don't go back to the parent metadata, it is scanned for the parent
                    keys.extend(search_deep_keys(search_text, obj[key], pathprop))
            elif isinstance(obj[key], list):
                for index, item in enumerate(obj[key]):
                    pathproparr = pathprop[:]
                    pathproparr.append(index)
                    keys.extend(search_deep_keys(search_text, item, pathproparr))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            pathprop = path[:]
            pathprop.append(index)
            keys.extend(search_deep_keys(search_text, item, pathprop))

    return keys


def find_in_dict(input_dict: Dict[str, Any], key_path: str) -> Any:
    """Tries to retrieve the value under the given 'key_path', otherwise returns None."""

    value = input_dict
    key_list = key_path.split("/")

    try:
        for key in key_list:
            if key.startswith("[") and key.endswith("]"):
                if isinstance(value, list):
                    idx = int(key[1:-1])
                    value = value[idx]
                    continue
                else:
                    return None

            value = value.get(key)
            if value is None:
                return None
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        logging.debug(f"Could not find {key_path} in dict")
        return None

    return value
