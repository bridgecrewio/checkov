import dpath

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSLoggingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure AKS logging to Azure Monitoring is Configured"
        id = "CKV_AZURE_4"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        self.provider_version_2_path = "addon_profile/[0]/oms_agent/[0]/enabled"
        self.provider_version_3_path = "oms_agent/[0]/log_analytics_workspace_id"
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if dpath.search(conf, self.provider_version_2_path):
            self.evaluated_keys = [self.provider_version_2_path]
            return super().scan_resource_conf(conf)
        elif dpath.search(conf, self.provider_version_3_path):
            self.evaluated_keys = [self.provider_version_3_path]
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_inspected_key(self) -> str:
        return self.provider_version_2_path


check = AKSLoggingEnabled()
