from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

class K8SPublicIP(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kubernetes cluster does not have public IP address."
        id = "CKV_YC_5"
        categories = [CheckCategories.NETWORKING]
        supported_resources = ["yandex_kubernetes_cluster"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "master/[0]/public_ip"

    def get_forbidden_values(self) -> List[Any]:
        return [True]

check = K8SPublicIP()