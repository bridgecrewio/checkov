import hashlib
import json
from typing import Union, List, Dict, Any


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