from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class NkSPublicAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure NCP EKS public endpoint disabled"
        id = "CKV_NCP_19"
        supported_resources = ("ncloud_nks_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network"

    def get_expected_value(self) -> Any:
        return False


check = NkSPublicAccess()