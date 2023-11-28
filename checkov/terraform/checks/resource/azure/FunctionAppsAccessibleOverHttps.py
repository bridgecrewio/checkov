from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class FunctionAppsAccessibleOverHttps(BaseResourceCheck):

    def __init__(self) -> None:
        name = "Ensure that Function apps is only accessible over HTTPS"
        id = "CKV_AZURE_70"
        supported_resources = ['azurerm_function_app', 'azurerm_linux_function_app', 'azurerm_windows_function_app',
                               'azurerm_function_app_slot', 'azurerm_linux_function_app_slot',
                               'azurerm_windows_function_app_slot']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # default=false for https_only
        if 'https_only' not in conf.keys():
            return CheckResult.FAILED

        https_only = conf.get('https_only')[0]
        if not https_only:
            return CheckResult.FAILED

        # relevant for linux/windows resources
        if 'auth_settings_v2' in conf.keys():
            auth_settings_v2 = conf['auth_settings_v2'][0]

            # default=true for require_https
            if 'require_https' not in auth_settings_v2.keys():
                return CheckResult.PASSED

            require_https = auth_settings_v2.get('require_https')[0]
            if not require_https:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = FunctionAppsAccessibleOverHttps()
