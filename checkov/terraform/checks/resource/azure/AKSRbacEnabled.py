import dpath.util
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSRbacEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure RBAC is enabled on AKS clusters"
        id = "CKV_AZURE_5"
        supported_resources = ["azurerm_kubernetes_cluster"]
        categories = [CheckCategories.KUBERNETES]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        self.evaluated_keys = [
            "role_based_access_control/[0]/enabled",  # azurerm < 2.99.0
            "role_based_access_control_enabled",  # azurerm >= 2.99.0
        ]

        for key in self.evaluated_keys:
            if dpath.search(conf, key):
                return CheckResult.PASSED if dpath.get(conf, key)[0] else CheckResult.FAILED

        return CheckResult.PASSED


check = AKSRbacEnabled()
