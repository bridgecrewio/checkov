from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityRequirement(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_6"
        name = "Ensure that security requirement in securityDefinitions are defined."
        categories = [CheckCategories.APPLICATION_SECURITY]
        supported_resources = ['securityDefinitions']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        self.evaluated_keys = ["securityDefinitions"]
        if "securityDefinitions" not in conf:
            return CheckResult.FAILED, conf

        security_definitions = conf["securityDefinitions"]
        if not security_definitions or ('__startline__' in security_definitions and len(security_definitions) <= 2):
            return CheckResult.FAILED, security_definitions

        # apikey exists
        if 'api_key' not in security_definitions \
                or not self.are_fields_exist(set(security_definitions['api_key'].keys()), {'type', 'name', 'in'}):
            return CheckResult.FAILED, security_definitions

        # OAuth2 exists
        if 'petstore_auth' not in security_definitions \
                or not self.are_fields_exist(set(security_definitions['petstore_auth'].keys()), {'type', 'flow', 'authorizationUrl', 'scopes'}):
            return CheckResult.FAILED, security_definitions

        return CheckResult.PASSED, conf

    def are_fields_exist(self, keys: set[str], fields: set[str]) -> bool:
        """ if "keys" set contains "fields" """
        return len(fields & keys) == len(fields)

check = SecurityRequirement()
