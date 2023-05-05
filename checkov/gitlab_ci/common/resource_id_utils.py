from __future__ import annotations
from typing import Any

from checkov.common.util.consts import START_LINE, END_LINE

IMAGE_BLOCK_NAMES = ('image', 'services')
SKIP_BLOCKS = ('include', 'stages', 'cache', 'variables')


def generate_resource_key_recursive(conf: dict[str, Any] | list[str] | str, key: str, start_line: int,
                                    end_line: int) -> str:
    return _generate_resource_key_recursive(conf, key, start_line, end_line, set(), 0)


def _generate_resource_key_recursive(conf: dict[str, Any] | list[str] | str, key: str, start_line: int,
                                     end_line: int, scanned_image_blocks: set[str], depth: int) -> str:
    if not isinstance(conf, dict):
        return key

    for k, value in conf.items():
        if depth == 0 and k in SKIP_BLOCKS:
            continue

        if k in IMAGE_BLOCK_NAMES:
            scanned_image_blocks.add(k)

        if isinstance(value, dict) and value[START_LINE] <= start_line <= end_line <= value[END_LINE]:
            next_key = f'{key}.{k}' if key else k
            return _generate_resource_key_recursive(value, next_key, start_line, end_line, scanned_image_blocks,
                                                    depth + 1)

        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                next_key = f'{key}.{k}' if key else k

                for idx, entry in enumerate(value):
                    if entry and isinstance(entry, dict) and entry[START_LINE] <= start_line <= end_line <= entry[END_LINE]:
                        next_key += f'.{idx + 1}'
                        break  # There can be only one match in terms of line range

                return _generate_resource_key_recursive(value, next_key, start_line, end_line, scanned_image_blocks,
                                                        depth + 1)

        if any(block_name in conf.keys()
               and block_name not in scanned_image_blocks
               and isinstance(conf[block_name], dict)
               and conf[block_name].get(START_LINE) <= start_line
               and conf[block_name].get(END_LINE) >= end_line
               for block_name in IMAGE_BLOCK_NAMES):
            # Avoid settling for a too general resource id, when there are blocks which usually contain image names,
            # and that these blocks were not scanned yet & match the line range.
            continue

        if depth == 0:
            # Indicates the first recursive call. a heuristic that top-level entities should usually be disregarded
            # in case they are not dictionaries.
            continue

        if isinstance(value, list):
            if key:
                return f'{key}.{k}'
            else:
                continue
        if isinstance(value, str):
            return key

    return key
