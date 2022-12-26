from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class Oauth2SecurityPasswordFlow(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_8"
        name = "Ensure that security is not using 'password' flow in OAuth2 authentication - version 2.0 files"
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
        security_values = conf.get("security") or [{}]
        security_definitions = conf.get('securityDefinitions') or {}

        for auth_dict in security_values:
            if not isinstance(auth_dict, dict):
                return CheckResult.UNKNOWN, conf
            for auth_key in auth_dict:
                if self.is_start_end_line(auth_key):
                    continue
                if not isinstance(security_definitions, dict):
                    return CheckResult.UNKNOWN, conf
                auth_definition = security_definitions.get(auth_key, {})
                auth_type = auth_definition.get('type', '')
                if auth_type.lower() == 'oauth2':
                    auth_flow = auth_definition.get('flow', '')
                    if auth_flow == 'password':
                        return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2SecurityPasswordFlow()
