from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class FunctionAppsAccessibleOverHttps(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Function apps is only accessible over HTTPS"
        id = "CKV_AZURE_70"
        supported_resources = (
            "Microsoft.Web/sites/config",
            "Microsoft.Web/sites",
            "Microsoft.Web/sites/slots",
        )
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        is_site = self.entity_type in ("Microsoft.Web/sites", "Microsoft.Web/sites/slots")

        if not isinstance(properties, dict):
            # a site or slot without properties has no httpsOnly, so it is not restricted to HTTPS
            if is_site:
                return CheckResult.FAILED
            # a sites/config resource without properties (e.g. a conditional Bicep resource) can't be evaluated
            return CheckResult.UNKNOWN

        if is_site:
            if not properties.get("httpsOnly"):
                return CheckResult.FAILED

        if "httpSettings" in properties:
            auth_settings_v2 = properties["httpSettings"]

            # default=true for require_https
            if 'requireHttps' not in auth_settings_v2:
                return CheckResult.PASSED

            require_https = auth_settings_v2.get("requireHttps")
            if not require_https:
                return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/httpsOnly", "properties/httpSettings"]


check = FunctionAppsAccessibleOverHttps()
