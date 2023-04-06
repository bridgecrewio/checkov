from __future__ import annotations

import logging
from collections.abc import Hashable
from pathlib import Path
from typing import Tuple, Dict, Any, List, TYPE_CHECKING

import yaml
from charset_normalizer import from_path
from yaml.loader import SafeLoader

if TYPE_CHECKING:
    from yaml import MappingNode

logger = logging.getLogger(__name__)


def loads(content: str) -> list[dict[str, Any]]:
    """
    Load the given YAML string
    """

    content = "[" + content + "]"
    content = content.replace('}{', '},{')
    content = content.replace('}\n{', '},\n{')

    template: list[dict[str, Any]] = yaml.load(content, Loader=SafeLineLoader)  # nosec  # custom safe loader

    # Convert an empty file to an empty dict
    if template is None:
        template = []

    return template


def load(filename: Path) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
    """
    Load the given JSON file
    """

    file_path = filename if isinstance(filename, Path) else Path(filename)

    try:
        content = file_path.read_text()
    except UnicodeDecodeError:
        logger.debug(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
        content = str(from_path(file_path).best())

    if not all(key in content for key in ("apiVersion", "kind")):
        return [{}], []

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    template = loads(content)

    return template, file_lines


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        mapping = super().construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        # mapping['__line__'] = node.start_mark.line + 1
        mapping['__startline__'] = node.start_mark.line + 1
        mapping['__endline__'] = node.end_mark.line + 1
        return mapping
