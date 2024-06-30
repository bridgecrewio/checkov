from __future__ import annotations

from typing import Any

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
        if "properties" in conf:
            if self.entity_type == "Microsoft.Web/sites" or self.entity_type == "Microsoft.Web/sites/slots":
                if "httpsOnly" not in conf["properties"]:
                    return CheckResult.FAILED

                https_only = conf["properties"]["httpsOnly"]
                if not https_only:
                    return CheckResult.FAILED

        if "httpSettings" in conf["properties"]:
            auth_settings_v2 = conf["properties"]["httpSettings"]

            # default=true for require_https
            if 'requireHttps' not in auth_settings_v2:
                return CheckResult.PASSED

            require_https = auth_settings_v2.get("requireHttps")
            if not require_https:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = FunctionAppsAccessibleOverHttps()
