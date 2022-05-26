from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2019-08-01/sites/config-authsettings


class AppServiceAuthentication(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure App Service Authentication is set on Azure App Service"
        id = "CKV_AZURE_13"
        supported_resources = ("Microsoft.Web/sites/config", "config")
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if self.entity_type == "Microsoft.Web/sites/config":
            if "name" in conf and "authsettings" in conf["name"]:
                if "properties" in conf and "enabled" in conf["properties"]:
                    if str(conf["properties"]["enabled"]).lower() == "true":
                        return CheckResult.PASSED
            return CheckResult.FAILED
        elif self.entity_type == "config":
            if "name" in conf and conf["name"] == "authsettings":
                if "parent_type" in conf:
                    if conf["parent_type"] == "Microsoft.Web/sites":
                        if "properties" in conf:
                            if "enabled" in conf["properties"]:
                                if str(conf["properties"]["enabled"]).lower() == "true":
                                    return CheckResult.PASSED
                    return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = AppServiceAuthentication()
