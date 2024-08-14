from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class FunctionAppsEnableAuthentication(BaseResourceCheck):

    def __init__(self) -> None:
        name = "Ensure that function apps enables Authentication"
        id = "CKV_AZURE_56"
        supported_resources = ("Microsoft.Web/sites/config",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get('name', '') != 'authsettingsV2':
            return CheckResult.PASSED

        properties = conf.get('properties', {})
        if properties and isinstance(properties, dict):
            platform = properties.get('platform', {})
            if platform and isinstance(properties, dict):
                enabled = platform.get('enabled', False)
                if enabled:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = FunctionAppsEnableAuthentication()
