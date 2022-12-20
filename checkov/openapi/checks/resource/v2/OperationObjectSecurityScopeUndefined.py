from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class OperationObjectSecurityScopeUndefined(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_21"
        name = "Ensure that security scopes of operations are defined in securityDefinitions - version 2.0 files"
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
        paths = conf.get("paths", {})
        security_definitions = conf.get('securityDefinitions', {}) or {}

        for path, path_dict in paths.items():
            if self.is_start_end_line(path):
                continue
            for operation, operation_dict in path_dict.items():
                if self.is_start_end_line(operation):
                    continue
                op_security = operation_dict.get('security', [{}])
                for security in op_security:
                    for auth_key, auth_scopes in security.items():
                        if self.is_start_end_line(auth_key):
                            continue
                        auth_definition = security_definitions.get(auth_key, {})
                        if not auth_definition:
                            return CheckResult.FAILED, conf
                        definition_scopes = auth_definition.get('scopes', {})
                        if not definition_scopes:
                            return CheckResult.FAILED, conf
                        for scope in auth_scopes:
                            if scope not in definition_scopes:
                                return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = OperationObjectSecurityScopeUndefined()
