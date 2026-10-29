from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


def _is_enabled(value: Any) -> bool:
    # APIM customProperties are string flags in ARM templates (e.g. "false"),
    # so a plain truthiness check would treat "false" as enabled.
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false")
    return bool(value)


class APIManagementMinTLS12(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API management uses at least TLS 1.2"
        id = "CKV_AZURE_173"
        supported_resources = ("Microsoft.ApiManagement/service",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if isinstance(properties, dict) and "customProperties" in properties:
            self.evaluated_keys = ["properties"]
            customProperties = properties.get("customProperties")
            if isinstance(customProperties, dict):
                self.evaluated_keys = ["properties/customProperties"]
                if _is_enabled(customProperties.get("Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Ssl30")):
                    return CheckResult.FAILED
                if _is_enabled(customProperties.get("Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls10")):
                    return CheckResult.FAILED
                if _is_enabled(customProperties.get("Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Ssl30")):
                    return CheckResult.FAILED
                if _is_enabled(customProperties.get("Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10")):
                    return CheckResult.FAILED
                if _is_enabled(customProperties.get("Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11")):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = APIManagementMinTLS12()
