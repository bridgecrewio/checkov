from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class ClearTestAPIKey(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_20"
        name = "Ensure that API keys are not sent over cleartext"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['paths']
        self.irrelevant_keys = ['__startline__', '__endline__']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        if conf.get("components"):
            components = conf.get("components", {}) or {}
            security_schemes = components.get("securitySchemes", {}) or {}
        elif conf.get("securityDefinitions"):
            security_schemes = conf.get("securityDefinitions", {}) or {}

        paths = conf.get('paths', {}) or {}

        filtered_dict = {}
        for name, scheme in security_schemes.items():
            if isinstance(scheme, dict) and "type" in scheme and scheme['type'] == "apiKey":
                filtered_dict[name] = scheme
        if not filtered_dict:
            return CheckResult.PASSED, security_schemes

        if not isinstance(paths, dict):
            return CheckResult.PASSED, security_schemes
        for key, path in paths.items():
            if not path:
                continue
            if key in self.irrelevant_keys:
                continue
            for _operation, value in path.items():
                if not isinstance(value, dict):
                    continue
                if value.get('security'):
                    for sec in value['security'][0]:
                        if sec in filtered_dict:
                            return CheckResult.FAILED, security_schemes
        return CheckResult.PASSED, conf


check = ClearTestAPIKey()
