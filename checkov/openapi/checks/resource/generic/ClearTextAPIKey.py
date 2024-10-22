from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class ClearTestAPIKey(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_20"
        name = "Ensure that API keys are not sent over cleartext"
        categories = (CheckCategories.API_SECURITY,)
        supported_resources = ('paths',)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        schemes = conf.get("schemes")
        if schemes and isinstance(schemes, list):
            if "http" not in schemes and "ws" not in schemes:
                return CheckResult.PASSED, conf

        servers = conf.get("servers")
        if servers and isinstance(servers, list):
            if not any(server['url'].startswith('http://') for server in servers) and \
               not any(server['url'].startswith('ws://') for server in servers):
                return CheckResult.PASSED, conf

        components = conf.get("components")
        security_def = conf.get("securityDefinitions")
        if components and isinstance(components, dict):
            security_schemes = components.get("securitySchemes") or {}
        elif security_def:
            security_schemes = security_def
        else:
            return CheckResult.PASSED, conf

        paths = conf.get('paths')
        if not isinstance(paths, dict):
            return CheckResult.PASSED, security_schemes

        filtered_dict = {}
        if isinstance(security_schemes, dict):
            for name, scheme in security_schemes.items():
                if isinstance(scheme, dict) and scheme.get('type') == "apiKey":
                    filtered_dict[name] = scheme

        if not filtered_dict:
            return CheckResult.PASSED, security_schemes

        for key, path in paths.items():
            if not path:
                continue
            if key in LINE_FIELD_NAMES:
                continue
            for value in path.values():
                if not isinstance(value, dict):
                    continue
                operation_security = value.get('security')
                if operation_security and isinstance(operation_security, list):
                    for sec in operation_security[0]:
                        if sec in filtered_dict:
                            return CheckResult.FAILED, security_schemes

        return CheckResult.PASSED, conf


check = ClearTestAPIKey()
