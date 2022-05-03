from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

class K8SAutoUpgrade(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kubernetes cluster auto-upgrade is enabled."
        id = "CKV_YC_7"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ["yandex_kubernetes_cluster"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self):
        return "master/[0]/maintenance_policy/[0]/auto_upgrade"

    def get_forbidden_values(self) -> List[Any]:
        return [False]

check = K8SAutoUpgrade()