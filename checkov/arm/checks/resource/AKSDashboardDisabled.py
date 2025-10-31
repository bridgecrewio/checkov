from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AKSDashboardDisabled(BaseResourceCheck):
    def __init__(self) -> None:
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure Kubernetes Dashboard is disabled"
        id = "CKV_AZURE_8"
        supported_resources = ('Microsoft.ContainerService/managedClusters',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get("apiVersion") is not None:
            if conf["apiVersion"] == "2017-08-31":
                # No addonProfiles option to configure
                self.evaluated_keys = ["apiVersion"]
                return CheckResult.FAILED

        properties = conf.get("properties")
        self.evaluated_keys = ["properties"]
        if properties is None or not isinstance(properties, dict):
            self.evaluated_keys = ["properties"]
            return CheckResult.FAILED
        addon_profiles = conf["properties"].get("addonProfiles")
        if not isinstance(addon_profiles, dict):
            self.evaluated_keys = ["properties/addonProfiles"]
            return CheckResult.FAILED
        kube_dashboard = addon_profiles.get("kubeDashboard")
        if not isinstance(kube_dashboard, dict):
            self.evaluated_keys = ["properties/addonProfiles/kubeDashboard"]
            return CheckResult.FAILED
        enabled = kube_dashboard.get("enabled")
        if enabled is not None and str(enabled).lower() == "false":
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSDashboardDisabled()
