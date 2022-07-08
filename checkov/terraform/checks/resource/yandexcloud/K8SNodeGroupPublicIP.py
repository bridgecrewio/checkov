from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

class K8SNodeGroupPublicIP(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kubernetes cluster node group does not have public IP addresses."
        id = "CKV_YC_6"
        categories = [CheckCategories.NETWORKING]
        supported_resources = ["yandex_kubernetes_node_group"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "instance_template/[0]/network_interface/[0]/nat"

    def get_forbidden_values(self) -> List[Any]:
        return [True]

check = K8SNodeGroupPublicIP()