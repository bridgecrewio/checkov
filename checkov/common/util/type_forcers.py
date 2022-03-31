import json
import logging
from json import JSONDecodeError
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
    except Exception:
        return None


def force_float(var: Any) -> Optional[float]:
    try:
        if not isinstance(var, float):
            return float(var)
        return var
    except Exception:
        return None


def convert_str_to_bool(bool_str: Union[bool, str]) -> Union[bool, str]:
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


def extract_policy_dict(policy: Union[dict, str]) -> Optional[dict]:
    if isinstance(policy, dict):
        return policy
    if isinstance(policy, str):
        try:
            policy_dict = json.loads(policy)
            return policy_dict
        except JSONDecodeError:
            return None

    return None


def convert_csv_string_arg_to_list(csv_string_arg: Union[List[str], str, None]) -> list:
    """
    Converts list type arguments that also support comma delimited strings into a list.
    For instance the --check flag in the CLI:
        checkov -c CKV_1,CKV2
        will translate to ['CKV_1', 'CKV_2']
    :param csv_string_arg: Comma delimited string
    :return: List of strings or empty list
    """
    if csv_string_arg is None:
        return []
    if isinstance(csv_string_arg, str):
        return csv_string_arg.split(',')
    elif isinstance(csv_string_arg, list) and len(csv_string_arg) == 1:
        return csv_string_arg[0].split(',')
    else:
        return csv_string_arg
