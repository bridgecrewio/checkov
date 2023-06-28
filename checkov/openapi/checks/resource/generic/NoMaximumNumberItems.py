from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class NoMaximumNumberItems(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_21"
        name = "Ensure that arrays have a maximum number of items"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['paths']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:  # type:ignore[override]  # return type is different than the base class
        queue = [conf]
        key = 'type'

        while queue:
            current_dict = queue.pop(0)
            if key in current_dict:
                if current_dict['type'] == 'array' and current_dict.get('maxItems') is None:
                    return CheckResult.FAILED, current_dict
            for k, v in current_dict.items():
                if isinstance(v, dict):
                    queue.append(v)
                if isinstance(v, list):
                    for dict2 in v:
                        queue.append(dict2)

        return CheckResult.PASSED, conf


check = NoMaximumNumberItems()
