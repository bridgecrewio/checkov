from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.parsers.node import DictNode


class AKSRbacEnabled(BaseResourceCheck):
    def __init__(self):
        # apiVersion 2017-08-03 = Fail - No enableRBAC option to configure
        name = "Ensure RBAC is enabled on AKS clusters"
        id = "CKV_AZURE_5"
        supported_resources = ['Microsoft.ContainerService/managedClusters']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "apiVersion" in conf:
            if conf["apiVersion"] == "2017-08-31":
                # No enableRBAC option to configure
                return CheckResult.FAILED

        properties = conf.get('properties')
        if not properties or not isinstance(properties, DictNode):
            return CheckResult.FAILED
        enable_RBAC = properties.get('enableRBAC')
        if str(enable_RBAC).lower() == "true":
            return CheckResult.PASSED
        return CheckResult.FAILED

check = AKSRbacEnabled()
