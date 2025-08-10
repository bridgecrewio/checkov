from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AKSLoggingEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure AKS logging to Azure Monitoring is Configured"
        id = "CKV_AZURE_4"
        supported_resources = ("Microsoft.ContainerService/managedClusters",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "apiVersion" in conf:
            if conf["apiVersion"] == "2017-08-31":
                self.evaluated_keys = ["apiVersion"]
                # No addonProfiles option to configure
                return CheckResult.FAILED

        properties = conf.get("properties")
        self.evaluated_keys = ["properties"]
        if isinstance(properties, dict):
            addon_profiles = properties.get("addonProfiles")
            if isinstance(addon_profiles, dict):
                self.evaluated_keys = ["properties/addonProfiles"]
                omsagent = addon_profiles.get("omsagent")
                if not omsagent:
                    # it can be written in lowercase or camelCase
                    omsagent = addon_profiles.get("omsAgent")

                if isinstance(omsagent, dict) and omsagent.get("enabled"):
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = AKSLoggingEnabled()
