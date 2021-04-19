from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

class AKSDashboardDisabled(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure Kubernetes Dashboard is disabled"
        id = "CKV_AZURE_8"
        supported_resources = ['Microsoft.ContainerService/managedClusters']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "apiVersion" in conf:
            if conf["apiVersion"] == "2017-08-31":
                # No addonProfiles option to configure
                return CheckResult.FAILED

        if "properties" in conf:
            if "addonProfiles" in conf["properties"]:
                if "kubeDashboard" in conf["properties"]["addonProfiles"]:
                    if "enabled" in conf["properties"]["addonProfiles"]["kubeDashboard"]:
                        if str(conf["properties"]["addonProfiles"]["kubeDashboard"]["enabled"]).lower() == "false":
                            return CheckResult.PASSED

        return CheckResult.FAILED

check = AKSDashboardDisabled()