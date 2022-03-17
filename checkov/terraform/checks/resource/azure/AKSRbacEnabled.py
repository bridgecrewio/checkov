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
        # azurerm < 2.99.0
        inspected_key1 = "role_based_access_control/[0]/enabled"
        # azurerm >= 2.99.0
        inspected_key2 = "role_based_access_control_enabled"
        rbac_enabled = False

        if dpath.search(conf, inspected_key1) != {}:
            rbac_enabled = dpath.get(conf, inspected_key1)[0]
        elif dpath.search(conf, inspected_key2) != {}:
            rbac_enabled = dpath.get(conf, inspected_key2)[0]

        if rbac_enabled:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = AKSRbacEnabled()
