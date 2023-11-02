from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class NoMaximumNumberItems(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_21"
        name = "Ensure that arrays have a maximum number of items"
        categories = (CheckCategories.API_SECURITY,)
        supported_resources = ('paths',)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        result = self.check_array_max_items(inner_conf=conf)
        if result:
            return result

        return CheckResult.PASSED, conf

    def check_array_max_items(self, inner_conf: Any) -> tuple[CheckResult, dict[str, Any]] | None:
        if isinstance(inner_conf, dict):
            if "type" in inner_conf:
                if inner_conf["type"] == "array" and inner_conf.get("maxItems") is None:
                    return CheckResult.FAILED, inner_conf
            for value in inner_conf.values():
                if isinstance(value, dict):
                    result = self.check_array_max_items(inner_conf=value)
                    if result:
                        return result
                if isinstance(value, list):
                    for inner_conf_2 in value:
                        result = self.check_array_max_items(inner_conf=inner_conf_2)
                        if result:
                            return result

        return None


check = NoMaximumNumberItems()
