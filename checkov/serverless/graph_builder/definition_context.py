from __future__ import annotations

from typing import Any


def build_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[tuple[int, str]]]
                              ) -> dict[str, dict[str, Any]]:
    return {}


def add_resource_to_definitions_context(definitions_context: dict[str, dict[str, Any]], resource_key: str,
                                        resource_attributes: dict[str, Any], definition_attribute: str,
                                        definitions_raw: dict[str, Any], file_path: str) -> None:
    pass
