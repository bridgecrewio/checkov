from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.resource.v3.BaseOpenapiCheckV3 import BaseOpenapiCheckV3


class CleartextCredsOverUnencryptedChannel(BaseOpenapiCheckV3):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_3"
        name = "Ensure that security schemes don't allow cleartext credentials over unencrypted channel - version 3.x.y files"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ["components"]
        self.irrelevant_keys = ['__startline__', '__endline__']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        components = conf.get("components", {}) or {}
        security_schemes = components.get("securitySchemes", {}) or {}
        paths = conf.get('paths', {}) or {}

        if isinstance(security_schemes, list):
            security_schemes = security_schemes[0]
        for name, security_scheme in security_schemes.items():
            if name in self.irrelevant_keys:
                continue
            if isinstance(security_scheme, dict) and (security_scheme.get('type') == 'http' or security_scheme.get('scheme') == 'basic'):
                return CheckResult.FAILED, security_scheme

        if not isinstance(paths, dict):
            return CheckResult.PASSED, security_schemes
        for key, path in paths.items():
            if not path:
                continue
            if key in self.irrelevant_keys:
                continue
            for operation in path:
                if not isinstance(operation, dict):
                    continue
                if operation.get('security'):
                    return CheckResult.FAILED, security_schemes

        return CheckResult.PASSED, conf


check = CleartextCredsOverUnencryptedChannel()
