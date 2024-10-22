from __future__ import annotations

from typing import Dict, Any

from checkov.common.graph.checks_infra.base_check import BaseGraphCheck


class BaseGraphCheckParser:
    def validate_check_config(self, file_path: str, raw_check: dict[str, dict[str, Any]]) -> bool:
        """Validates the graph check config"""
        return True

    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> BaseGraphCheck:
        raise NotImplementedError
