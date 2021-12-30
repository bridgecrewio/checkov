from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSDashboardDisabled(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Kubernetes Dashboard is disabled"
        id = "CKV_AZURE_8"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        addon_profile = conf.get('addon_profile', [None])[0]
        self.evaluated_keys = ['addon_profile']
        if addon_profile and isinstance(addon_profile, dict):
            dashboard = addon_profile.get('kube_dashboard', [[]])[0]
            if isinstance(dashboard, dict) and dashboard.get('enabled', [False])[0]:
                self.evaluated_keys = ['addon_profile/kube_dashboard', 'addon_profile/kube_dashboard/[0]/enabled']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AKSDashboardDisabled()
