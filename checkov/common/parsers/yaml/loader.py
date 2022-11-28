from __future__ import annotations

from collections.abc import Hashable
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml
from yaml.loader import SafeLoader

if TYPE_CHECKING:
    from yaml import MappingNode


def loads(content: str) -> list[dict[str, Any]]:
    """
    Load the given YAML string
    """

    template = list(yaml.load_all(content, Loader=SafeLineLoader))

    # Convert an empty file to an empty dict
    if template is None:
        template = {}

    return template


def load(filename: str | Path, content: str | None = None) -> tuple[list[dict[str, Any]], list[tuple[int, str]]]:
    """
    Load the given YAML file
    """

    if not content:
        file_path = filename if isinstance(filename, Path) else Path(filename)
        content = file_path.read_text()

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

    bool_values = {  # noqa: CCE003  # used to override the SafeLoader default behaviour
        'yes': True,
        'no': False,
        'true': True,
        'false': False,
        # GHA workflow files have a saved word for "on". Since we have policies inspecting the "on" section we need
        # to keep the string value.
        'on': 'on',  # type:ignore[dict-item]
        'off': False,
    }


class SafeLineLoaderGhaSchema(SafeLoader):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        return super().construct_mapping(node, deep=deep)

    bool_values = {  # noqa: CCE003  # used to override the SafeLoader default behaviour
        'on': 'on',  # type:ignore[dict-item]
        'off': 'off',  # type:ignore[dict-item]
        'yes': 'true',  # type:ignore[dict-item]
        'no': 'false',  # type:ignore[dict-item]
        'true': 'true',  # type:ignore[dict-item]
        'false': 'false'  # type:ignore[dict-item]
    }
