import logging
import os
from typing import Optional, List, Tuple, Dict, Any, Union

from checkov.common.parsers.node import DictNode, ListNode, StrNode


def build_definitions_context(
        definitions: Dict[str, DictNode], definitions_raw: Dict[str, List[Tuple[int, str]]]
) -> Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    for file_path, file_path_definitions in definitions.items():
        print(file_path)
        print(file_path_definitions)
        pass
