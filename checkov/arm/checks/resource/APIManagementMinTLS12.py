from __future__ import annotations
from typing import Any
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class APIManagementMinTLS12(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API management uses at least TLS 1.2"
        id = "CKV_AZURE_173"
        supported_resources = ("Microsoft.ApiManagement/service",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('properties', {})
        if 'identity' in properties:
            identity = properties['identity']
            if 'enableFrontendTls10' in identity:
                if identity['enableFrontendTls10']:
                    return CheckResult.FAILED
            if 'enableFrontendTls11' in identity:
                if identity['enableFrontendTls11']:
                    return CheckResult.FAILED
            if 'enableBackendTls10' in identity:
                if identity['enableBackendTls10']:
                    return CheckResult.FAILED
            if 'enableBackendTls11' in identity:
                if identity['enableBackendTls11']:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = APIManagementMinTLS12()
