from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSOnlyCriticalPodsOnSystemNodes(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        Microsoft recommends to isolate critical system pods from application pods
        to prevent misconfigured or rogue application pods from accidentally killing system pods.

        This can be enforced by creating a dedicated system node pool with the CriticalAddonsOnly=true:NoSchedule taint
        to prevent application pods from being scheduled on system node pools.
        """
        name = "Ensure that only critical system pods run on system nodes"
        id = "CKV_AZURE_232"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "default_node_pool/[0]/only_critical_addons_enabled"


check = AKSOnlyCriticalPodsOnSystemNodes()
