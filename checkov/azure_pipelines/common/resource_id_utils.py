from __future__ import annotations

from typing import Any, Dict, List

from checkov.common.util.consts import START_LINE, END_LINE


def _get_resource_from_code_block(start_line: int, end_line: int, block_to_inspect: dict[str, Any], inspected_key: str | None) -> str | None:
    if block_to_inspect[START_LINE] <= start_line <= end_line <= block_to_inspect[END_LINE]:
        block_name = block_to_inspect.get('displayName',
                                          block_to_inspect.get('name',
                                                               block_to_inspect.get('job',
                                                                                    block_to_inspect.get('stage',
                                                                                                         False))))
        inspected_key = f'{inspected_key}({block_name})' if block_name else inspected_key
        if block_to_inspect[START_LINE] == start_line:
            return inspected_key
        return generate_resource_key_recursive(start_line, end_line, block_to_inspect, resource_key=inspected_key)
    return None


def generate_resource_key_recursive(start_line: int, end_line: int,
                                    file_conf: Dict[str, Any] | List[Dict[str, Any]], resource_key: str | None = None
                                    ) -> str | None:
    if not isinstance(file_conf, dict):
        return resource_key

    for code_block_name, code_block in file_conf.items():
        if isinstance(code_block, dict):
            new_key = f'{resource_key}.{code_block_name}' if resource_key else code_block_name
            resource = _get_resource_from_code_block(start_line, end_line, code_block, new_key)
            if resource:
                return resource
        elif isinstance(code_block, list):
            for index, item in enumerate(code_block):
                if isinstance(item, dict):
                    resource_key_to_inspect = f'{resource_key}.{code_block_name}[{index}]' if resource_key else f'{code_block_name}[{index}]'
                    resource = _get_resource_from_code_block(start_line, end_line, item, resource_key_to_inspect)
                    if resource:
                        return resource
    return resource_key
