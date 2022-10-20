from __future__ import annotations
from typing import Any

from checkov.common.util.consts import START_LINE, END_LINE


def generate_resource_key_recursive(conf: dict[str, Any] | list[str] | str, key: str, start_line: int,
                                    end_line: int) -> str:
    if not isinstance(conf, dict):
        return key

    for k, value in conf.items():
        if isinstance(value, dict) and value[START_LINE] <= start_line <= end_line <= value[END_LINE]:
            return generate_resource_key_recursive(value, f'{key}.{k}' if key else k, start_line, end_line)
        # if k == START_LINE or k == END_LINE or isinstance(value, str):
        #     continue
        if isinstance(value, list):
            return f'{key}.{k}' if key else k
        if isinstance(value, str):
            return key

    return key
