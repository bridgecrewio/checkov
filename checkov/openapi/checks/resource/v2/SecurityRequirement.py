from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityRequirement(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_6"
        name = "Ensure that security requirement defined in securityDefinitions."
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        self.evaluated_keys = ["securityDefinitions"]
        if "securityDefinitions" not in conf:
            return CheckResult.FAILED, conf

        security_definitions = conf["securityDefinitions"]
        if not self.check_security_conf(conf, security_definitions):
            return CheckResult.FAILED, conf['security']

        paths = conf['paths']
        for path, http_method in paths.items():
            if self.is_start_end_line(path):
                continue
            for op_name, op_val in http_method.items():
                if self.is_start_end_line(op_name):
                    continue
                if not self.check_security_conf(op_val, security_definitions):
                    return CheckResult.FAILED, op_val['security']

        return CheckResult.PASSED, conf

    def check_security_conf(self, conf: dict[str, Any], security_definitions: dict[str, Any]) -> bool:
        self.evaluated_keys = ['security']
        return not('security' in conf and conf['security']
                   and not self.is_requirements_defined(conf['security'], security_definitions))

    def is_requirements_defined(self, security: list[dict[str, Any]], security_definitions: dict[str, Any]) -> bool:
        for scheme in security:
            for scheme_type, _ in scheme.items():
                if scheme_type not in security_definitions:
                    return False
        return True

check = SecurityRequirement()
