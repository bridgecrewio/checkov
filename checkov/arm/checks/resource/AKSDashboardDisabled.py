from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.parsers.node import DictNode

class AKSDashboardDisabled(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure Kubernetes Dashboard is disabled"
        id = "CKV_AZURE_8"
        supported_resources = ['Microsoft.ContainerService/managedClusters']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("apiVersion") is not None:
            if conf["apiVersion"] == "2017-08-31":
                # No addonProfiles option to configure
                return CheckResult.FAILED

        properties = conf.get("properties")
        if properties is None or not isinstance(properties, DictNode):
            return CheckResult.FAILED
        addon_profiles = conf["properties"].get("addonProfiles")
        if not isinstance(addon_profiles, DictNode):
            return CheckResult.FAILED
        kube_dashboard = addon_profiles.get("kubeDashboard")
        if not isinstance(kube_dashboard, DictNode):
            return CheckResult.FAILED
        enabled = kube_dashboard.get("enabled")
        if enabled is not None and str(enabled).lower() == "false":
            return CheckResult.PASSED
        return CheckResult.FAILED

check = AKSDashboardDisabled()