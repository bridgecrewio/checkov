from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class OperationObjectProducesUndefined(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_16"
        name = "Ensure that operation objects have 'produces' field defined for GET operations - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["paths"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        paths = conf.get('paths') or {}
        if not isinstance(paths, dict):
            return CheckResult.UNKNOWN, conf

        for path, path_dict in paths.items():
            if self.is_start_end_line(path):
                continue
            if not isinstance(path_dict, dict):
                return CheckResult.UNKNOWN, conf
            for operation, operation_dict in path_dict.items():
                if self.is_start_end_line(operation):
                    continue
                if operation.lower() == 'get':
                    if not isinstance(operation_dict, dict):
                        return CheckResult.UNKNOWN, conf
                    if not operation_dict.get('produces'):
                        return CheckResult.FAILED, operation_dict

        return CheckResult.PASSED, conf


check = OperationObjectProducesUndefined()
