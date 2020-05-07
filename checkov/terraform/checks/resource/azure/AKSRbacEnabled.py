from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSRbacEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure RBAC is enabled on AKS clusters"
        id = "CKV_AZURE_5"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'role_based_access_control' not in conf or conf['role_based_access_control'][0]['enabled'][0]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSRbacEnabled()
