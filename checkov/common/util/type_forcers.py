from __future__ import annotations

import json
import logging
import typing
from json import JSONDecodeError
from typing import TypeVar, overload, Any, Dict

import yaml

T = TypeVar("T")


@overload
def force_list(var: list[T]) -> list[T]:
    ...


@overload
def force_list(var: T) -> list[T]:
    ...


def force_list(var: T | list[T]) -> list[T]:
    if not isinstance(var, list):
        return [var]
    return var


def force_int(var: Any) -> int | None:
    try:
        if not isinstance(var, int):
            return int(var)
        return var
    except Exception:
        return None


def force_float(var: Any) -> float | None:
    try:
        if not isinstance(var, float):
            return float(var)
        return var
    except Exception:
        return None


def convert_str_to_bool(bool_str: bool | str) -> bool:
    if isinstance(bool_str, str):
        bool_str_lower = bool_str.lower()
        if bool_str_lower in ("true", '"true"'):
            return True
        elif bool_str_lower in ("false", '"false"'):
            return False

    # If we got here it must be a boolean, mypy doesn't understand it, so we use cast
    return typing.cast(bool, bool_str)


def force_dict(obj: Any) -> dict[str, Any] | None:
    """
    If the specified object is a dict, returns the object. If the specified object is a list or a tuple
    of length 1 or more, force_dict is called recursively on the first element. Else returns None.
    :param obj:
    :return:
    """
    if isinstance(obj, dict):
        return obj
    if (isinstance(obj, list) or isinstance(obj, tuple)) and len(obj) > 0:
        return force_dict(obj[0])
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


def extract_policy_dict(policy: Any) -> dict[str, Any] | None:
    if isinstance(policy, dict):
        return policy
    if isinstance(policy, str):
        try:
            policy_dict: dict[str, Any] = json.loads(policy)
            return policy_dict
        except JSONDecodeError:
            return None

    return None


def extract_json(json_str: Any) -> dict[str, Any] | list[dict[str, Any]] | None:
    """Tries to return a json object from a possible string value"""

    if isinstance(json_str, list):
        return json_str

    return extract_policy_dict(json_str)


def convert_csv_string_arg_to_list(csv_string_arg: list[str] | str | None) -> list[str]:
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


def convert_prisma_policy_filter_to_dict(filter_string: str) -> Dict[Any, Any]:
    """
    Converts the filter string to a dict. For example:
    'policy.label=label,cloud.type=aws' becomes -->
    {'policy.label': 'label1', 'cloud.type': 'aws'}
    Note that the API does not accept lists https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policies-v2
    This is not allowed: policy.label=label1,label2
    """
    filter_params = {}
    if isinstance(filter_string, str) and filter_string:
        filter_string = "".join(filter_string.split())
        try:
            for f in filter_string.split(','):
                f_name, f_value = f.split('=')
                filter_params[f_name] = f_value
        except (IndexError, ValueError) as e:
            logging.debug(f"Invalid filter format: {e}")
    return filter_params
