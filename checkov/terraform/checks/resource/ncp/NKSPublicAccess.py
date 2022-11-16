from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class NKSPublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Naver Kubernetes Service public endpoint disabled"
        id = "CKV_NCP_19"
        supported_resources = ("ncloud_nks_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'public_network'

    def get_forbidden_values(self):
        return [True]


check = NKSPublicAccess()
