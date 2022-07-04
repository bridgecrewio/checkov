import dpath

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class AKSLoggingEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AKS logging to Azure Monitoring is Configured"
        id = "CKV_AZURE_4"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        provider_version_2_path = "addon_profile/[0]/oms_agent/[0]/enabled"
        provider_version_3_path = "oms_agent/[0]"
        if dpath.search(conf, provider_version_2_path) and dpath.get(conf, provider_version_2_path)[0]:
            self.evaluated_keys = [provider_version_2_path]
            return CheckResult.PASSED
        elif dpath.search(conf, provider_version_3_path):
            self.evaluated_keys = [provider_version_3_path]
            return CheckResult.PASSED

        return CheckResult.FAILED


check = AKSLoggingEnabled()
