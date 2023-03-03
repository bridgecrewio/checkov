from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class OperationObjectBasicAuth(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_15"
        name = "Ensure that operation objects do not use basic auth - version 2.0 files"
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
        security_definitions = conf.get('securityDefinitions') or {}

        for path, path_dict in paths.items():
            if self.is_start_end_line(path):
                continue
            if not isinstance(path_dict, dict):
                return CheckResult.UNKNOWN, conf
            for operation, operation_dict in path_dict.items():
                if self.is_start_end_line(operation):
                    continue
                if not isinstance(operation_dict, dict):
                    return CheckResult.UNKNOWN, conf
                security = operation_dict.get('security', [])
                for security_definition in security:
                    for auth_key in security_definition:
                        if self.is_start_end_line(auth_key):
                            continue
                        if not isinstance(security_definitions, dict):
                            return CheckResult.UNKNOWN, conf
                        auth_definition = security_definitions.get(auth_key, {})
                        auth_type = auth_definition.get('type', '')
                        if auth_type == 'basic':
                            return CheckResult.FAILED, auth_definition

        return CheckResult.PASSED, conf


check = OperationObjectBasicAuth()
