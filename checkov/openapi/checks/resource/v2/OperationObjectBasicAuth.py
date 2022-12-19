from __future__ import annotations

from typing import Any, Union, List
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class OperationObjectBasicAuth(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_15"
        name = "Ensure that operation objects do not use basic auth - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["paths"]
        self.irrelevant_keys = ['__startline__', '__endline__']
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(  # type:ignore[override]
            self, conf: dict[str, Any], entity_type: str
    ) -> tuple[CheckResult, Union[dict[str, Any], List[Any]]]:
        paths = conf.get('paths', {}) or {}
        security_definitions = conf.get('securityDefinitions', {}) or {}

        for path, path_dict in paths.items():
            if path in self.irrelevant_keys:
                continue
            for operation, operation_dict in path_dict.items():
                if operation in self.irrelevant_keys:
                    continue
                security = operation_dict.get('security', [])
                for security_definition in security:
                    for auth_key in security_definition:
                        if auth_key in self.irrelevant_keys:
                            continue
                        auth_definition = security_definitions.get(auth_key, {})
                        auth_type = auth_definition.get('type', '')
                        if auth_type == 'basic':
                            return CheckResult.FAILED, auth_definition

        return CheckResult.PASSED, conf


check = OperationObjectBasicAuth()
