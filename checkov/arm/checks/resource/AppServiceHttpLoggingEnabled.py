from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.arm.utils import is_auth_settings_v2_config
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceHttpLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that App service enables HTTP logging"
        id = "CKV_AZURE_63"
        supported_resources = ["Microsoft.Web/sites/config"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if is_auth_settings_v2_config(conf):
            # the authentication settings child doesn't hold this setting
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "properties/httpLoggingEnabled"

    def get_expected_value(self) -> bool:
        return True


check = AppServiceHttpLoggingEnabled()
