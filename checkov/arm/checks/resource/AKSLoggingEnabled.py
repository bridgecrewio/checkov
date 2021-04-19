from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

class AKSLoggingEnabled(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure AKS logging to Azure Monitoring is Configured"
        id = "CKV_AZURE_4"
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
                if "omsagent" in conf["properties"]["addonProfiles"]:
                    if "enabled" in conf["properties"]["addonProfiles"]["omsagent"]:
                        if str(conf["properties"]["addonProfiles"]["omsagent"]["enabled"]).lower() == "true":
                            return CheckResult.PASSED

        return CheckResult.FAILED

check = AKSLoggingEnabled()