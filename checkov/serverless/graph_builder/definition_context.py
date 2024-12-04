from __future__ import annotations

from typing import cast, Dict, Any

from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.suppression import collect_suppressions_for_report




def build_definitions_context(definitions: dict[str, dict[str, Any]], definitions_raw: dict[str, list[tuple[int, str]]]
                              ) -> Dict[str, Dict[str, Any]]:
    return {}



def add_resource_to_definitions_context(definitions_context: dict[str, dict[str, Any]], resource_key: str,
                                        resource_attributes: dict[str, Any], definition_attribute: str,
                                        definitions_raw: dict[str, Any], file_path: str) -> None:
    pass
