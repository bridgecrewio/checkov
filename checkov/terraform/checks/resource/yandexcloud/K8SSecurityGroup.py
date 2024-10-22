from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class K8SSecurityGroup(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure security group is assigned to Kubernetes cluster."
        id = "CKV_YC_14"
        supported_resources = ("yandex_kubernetes_cluster",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "master/[0]/security_group_ids"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = K8SSecurityGroup()
