from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSDashboardDisabled(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Kube Dashboard is disabled"
        id = "CKV_AZURE_8"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        addon_profile = conf.get('addon_profile', [None])[0]
        if addon_profile and isinstance(addon_profile, dict):
            if addon_profile.get('kube_dashboard') and addon_profile['kube_dashboard'][0].get('enabled', [False])[0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AKSDashboardDisabled()
