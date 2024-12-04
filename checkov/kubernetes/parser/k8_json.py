from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, Dict, Any, List

import json
from checkov.common.parsers.json.decoder import SimpleDecoder
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import END_LINE, START_LINE
from checkov.common.util.file_utils import read_file_with_any_encoding

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def loads(content: str) -> list[dict[str, Any]]:
    """
    Load the given JSON string
    """

    content = "[" + content + "]"
    content = content.replace('}{', '},{')
    content = content.replace('}\n{', '},\n{')

    template: list[dict[str, Any]] = json.loads(content, cls=CustomDecoder)

    # Convert an empty file to an empty list
    if template is None:
        template = []

    return template


def load(filename: Path) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
    """
    Load the given JSON file
    """

    content = read_file_with_any_encoding(file_path=filename)

    if not all(key in content for key in ("apiVersion", "kind")):
        return [{}], []

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    template = loads(content)

    return template, file_lines


class CustomDecoder(SimpleDecoder):
    def object_hook(self, obj: dict[str, Any]) -> Any:
        obj[START_LINE] = 0
        obj[END_LINE] = 0
        return obj
