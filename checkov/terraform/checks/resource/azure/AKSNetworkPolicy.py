from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSNetworkPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AKS cluster has Network Policy configured"
        id = "CKV_AZURE_7"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'network_profile' in conf and conf['network_profile'][0].get('network_policy'):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSNetworkPolicy()
