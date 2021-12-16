from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.parsers.node import DictNode

class AKSLoggingEnabled(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No addonProfiles option to configure
        name = "Ensure AKS logging to Azure Monitoring is Configured"
        id = "CKV_AZURE_4"
        supported_resources = ['Microsoft.ContainerService/managedClusters']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("apiVersion"):
            if conf["apiVersion"] == "2017-08-31":
                # No addonProfiles option to configure
                return CheckResult.FAILED

        properties = conf.get("properties")
        if isinstance(properties, dict):
            addon_profiles = properties.get("addonProfiles")
            if isinstance(addon_profiles, dict):
                omsagent = addon_profiles.get("omsagent")
                if isinstance(omsagent, dict) and omsagent.get("enabled"):
                    return CheckResult.PASSED

        return CheckResult.FAILED

check = AKSLoggingEnabled()