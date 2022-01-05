from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AKSNetworkPolicy(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No networkProfile option to configure
        name = "Ensure AKS cluster has Network Policy configured"
        id = "CKV_AZURE_7"
        supported_resources = ['Microsoft.ContainerService/managedClusters']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "apiVersion" in conf:
            if conf["apiVersion"] == "2017-08-31":
                # No networkProfile option to configure
                return CheckResult.FAILED

        if "properties" in conf:
            if "networkProfile" in conf["properties"]:
                if "networkPolicy" in conf["properties"]["networkProfile"]:
                    if conf["properties"]["networkProfile"]["networkPolicy"]:
                        return CheckResult.PASSED
        return CheckResult.FAILED

check = AKSNetworkPolicy()
