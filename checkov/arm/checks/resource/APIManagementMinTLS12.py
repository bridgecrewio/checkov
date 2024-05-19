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
        if 'security' in properties:
            security = properties['security']
            if 'enableFrontendTls10' in security:
                if security['enableFrontendTls10']:
                    return CheckResult.FAILED
            if 'enableFrontendTls11' in security:
                if security['enableFrontendTls11']:
                    return CheckResult.FAILED
            if 'enableBackendTls10' in security:
                if security['enableBackendTls10']:
                    return CheckResult.FAILED
            if 'enableBackendTls11' in security:
                if security['enableBackendTls11']:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = APIManagementMinTLS12()

