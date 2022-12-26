from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class Oauth2SecurityDefinitionImplicitFlow(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_12"
        name = "Ensure no security definition is using implicit flow on OAuth2, which is deprecated - version 2.0 files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["securityDefinitions"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        security_definitions = conf.get('securityDefinitions') or {}

        for auth_key, auth_dict in security_definitions.items():
            if self.is_start_end_line(auth_key):
                continue
            if not isinstance(auth_dict, dict):
                return CheckResult.UNKNOWN, conf
            auth_type = auth_dict.get('type', '')
            if auth_type.lower() == 'oauth2':
                auth_flow = auth_dict.get('flow', '')
                if auth_flow == 'implicit':
                    return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2SecurityDefinitionImplicitFlow()
