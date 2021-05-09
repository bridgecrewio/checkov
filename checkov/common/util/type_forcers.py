import json
import logging
from typing import TypeVar, List, overload, Union, Optional, Any, Dict

import yaml

T = TypeVar("T")


@overload
def force_list(var: List[T]) -> List[T]:
    ...


@overload
def force_list(var: T) -> List[T]:
    ...


def force_list(var: Union[T, List[T]]) -> List[T]:
    if not isinstance(var, list):
        return [var]
    return var


def force_int(var: Any) -> Optional[int]:
    try:
        if not isinstance(var, int):
            return int(var)
        return var
    except:
        return None


def force_float(var: Any) -> Optional[float]:
    try:
        if not isinstance(var, float):
            return float(var)
        return var
    except:
        return None


def convert_str_to_bool(bool_str):
    if bool_str in ["true", '"true"', "True", '"True"']:
        return True
    elif bool_str in ["false", '"false"', "False", '"False"']:
        return False
    else:
        return bool_str


def force_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """
    If the specified object is a dict, returns the object. If the object is a list of length 1 or more, and the first
    element is a dict, returns the first element. Else returns None.
    :param obj:
    :return:
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict):
        return obj[0]
    return None


def is_json(data: str) -> bool:
    try:
        parsed = json.loads(data)
        return isinstance(parsed, dict)
    except (TypeError, ValueError):
        logging.debug(f"could not parse json data: {data}")
        return False


def is_yaml(data: str) -> bool:
    try:
        parsed = yaml.safe_load(data)
        return isinstance(parsed, dict)
    except yaml.YAMLError:
        logging.debug(f"could not parse yaml data: {data}")
        return False
