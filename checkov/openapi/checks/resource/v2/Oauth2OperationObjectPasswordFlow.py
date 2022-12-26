from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class Oauth2OperationObjectPasswordFlow(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_10"
        name = "Ensure that operation object does not use 'password' flow in OAuth2 authentication - version 2.0 files"
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
                    if not isinstance(security_definition, dict):
                        return CheckResult.UNKNOWN, conf
                    for auth_key, auth_definition in security_definitions.items():
                        if self.is_start_end_line(auth_key):
                            continue
                        if not isinstance(auth_definition, dict):
                            return CheckResult.UNKNOWN, conf
                        auth_type = auth_definition.get('type', '')
                        if auth_type.lower() == 'oauth2':
                            auth_flow = auth_definition.get('flow', '')
                            if auth_flow == 'password':
                                return CheckResult.FAILED, auth_definition

        return CheckResult.PASSED, conf


check = Oauth2OperationObjectPasswordFlow()
