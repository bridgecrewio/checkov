from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

class K8SNodeGroupAutoUpgrade(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kubernetes node group auto-upgrade is enabled."
        id = "CKV_YC_8"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ["yandex_kubernetes_node_group"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "maintenance_policy/[0]/auto_upgrade"

    def get_forbidden_values(self) -> List[Any]:
        return [False]

check = K8SNodeGroupAutoUpgrade()