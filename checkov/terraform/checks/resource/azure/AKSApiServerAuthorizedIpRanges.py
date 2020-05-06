from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSApiServerAuthorizedIpRanges(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AKS has an API Server Authorized IP Ranges enabled"
        id = "CKV_AZURE_6"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if len(conf.get('api_server_authorized_ip_ranges', [[]])[0]) > 0:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSApiServerAuthorizedIpRanges()
