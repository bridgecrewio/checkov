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
        addonProfiles = conf["properties"].get("addonProfiles")
        if not isinstance(addonProfiles, DictNode):
            return CheckResult.FAILED
        kubeDashboard = addonProfiles.get("kubeDashboard")
        if not isinstance(kubeDashboard, DictNode):
            return CheckResult.FAILED
        enabled = kubeDashboard.get("enabled")
        if enabled is None:
            return CheckResult.FAILED
        if str(enabled).lower() == "false":
            return CheckResult.PASSED
        return CheckResult.FAILED

check = AKSDashboardDisabled()