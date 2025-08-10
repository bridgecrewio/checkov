from __future__ import annotations

import logging
from collections.abc import Hashable
from pathlib import Path
from typing import Tuple, Dict, Any, List, TYPE_CHECKING

import json
import yaml
from yaml.loader import SafeLoader
from checkov.common.parsers.json.decoder import SimpleDecoder
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.consts import END_LINE, START_LINE, MAX_IAC_FILE_SIZE
from checkov.common.util.file_utils import read_file_with_any_encoding

if TYPE_CHECKING:
    from yaml import MappingNode

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def loads(content: str) -> list[dict[str, Any]]:
    """
    Load the given JSON string
    """

    content = "[" + content + "]"
    content = content.replace('}{', '},{')
    content = content.replace('}\n{', '},\n{')

    template: list[dict[str, Any]] = yaml.load(content, Loader=SafeLineLoader)  # nosec  # custom safe loader

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
    file_size = len(content)

    if file_size > MAX_IAC_FILE_SIZE:
        # large JSON files take too much time, when parsed with `pyyaml`, compared to a normal 'json.loads()'
        # with start/end line numbers of 0 takes only a few seconds
        logging.info(
            f"File {filename} has a size of {file_size} which is bigger than the supported 50mb, "
            "therefore file lines will default to 0."
            "This limit can be adjusted via the environment variable 'CHECKOV_MAX_IAC_FILE_SIZE'."
        )
        return json.loads(content, cls=CustomDecoder), file_lines

    template = loads(content)

    return template, file_lines


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        mapping = super().construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        # mapping['__line__'] = node.start_mark.line + 1
        mapping[START_LINE] = node.start_mark.line + 1
        mapping[END_LINE] = node.end_mark.line + 1
        return mapping


class CustomDecoder(SimpleDecoder):
    def object_hook(self, obj: dict[str, Any]) -> Any:
        obj[START_LINE] = 0
        obj[END_LINE] = 0
        return obj
