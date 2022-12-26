from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class GlobalSecurityScopeUndefined(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_19"
        name = "Ensure that global security scope is defined in securityDefinitions - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["security"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        security_definitions = conf.get('securityDefinitions') or {}
        security_values = conf.get('security') or [{}]
        for security in security_values:
            if not isinstance(security, dict):
                return CheckResult.UNKNOWN, conf
            for security_key, security_scopes in security.items():
                if self.is_start_end_line(security_key) or not security_scopes:
                    continue
                security_definition = security_definitions.get(security_key, {})
                if not security_definition:
                    return CheckResult.FAILED, conf
                definition_scopes = security_definition.get('scopes', {})
                if not definition_scopes:
                    return CheckResult.FAILED, conf
                for scope in security_scopes:
                    if scope not in definition_scopes:
                        return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = GlobalSecurityScopeUndefined()
