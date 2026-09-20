from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIManagementBackendHTTPS(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API management backend uses https"
        id = "CKV_AZURE_215"
        supported_resources = ("azurerm_api_management_backend",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["url"]
        url = conf.get("url")
        if url and isinstance(url, list):
            url_value = url[0]
            if not isinstance(url_value, str):
                return CheckResult.UNKNOWN
            if url_value.startswith("https://"):
                return CheckResult.PASSED
            if url_value.startswith("http://"):
                return CheckResult.FAILED
            return CheckResult.UNKNOWN
        return CheckResult.UNKNOWN


check = APIManagementBackendHTTPS()
