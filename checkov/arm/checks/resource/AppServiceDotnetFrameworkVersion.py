from __future__ import annotations

from typing import Any

from checkov.arm.utils import is_auth_settings_v2_config
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServiceDotnetFrameworkVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Net Framework' version is the latest, if used as a part of the web app"
        id = "CKV_AZURE_80"
        supported_resources = ['Microsoft.Web/sites/config']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if is_auth_settings_v2_config(conf):
            # the authentication settings child doesn't hold this setting
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "properties/netFrameworkVersion"

    def get_expected_value(self) -> str:
        return "v8.0"


check = AppServiceDotnetFrameworkVersion()
