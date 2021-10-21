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
        if conf.get("apiVersion") is not None:
            if conf["apiVersion"] == "2017-08-31":
                # No addonProfiles option to configure
                return CheckResult.FAILED
        
        if conf.get("properties") is not None:
            if isinstance(conf["properties"].get("addonProfiles"), DictNode):
                if conf["properties"]["addonProfiles"].get("omsagent") is not None:
                    if conf["properties"]["addonProfiles"]["omsagent"].get("enabled") is not None:
                        if str(conf["properties"]["addonProfiles"]["omsagent"]["enabled"]).lower() == "true":
                            return CheckResult.PASSED

        return CheckResult.FAILED

check = AKSLoggingEnabled()