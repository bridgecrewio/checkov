from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AKSLocalAdminDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AKS local admin account is disabled"
        id = "CKV_AZURE_141"
        supported_resources = ("Microsoft.ContainerService/managedClusters",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/disableLocalAccounts"

    def get_expected_value(self) -> bool:
        return True


check = AKSLocalAdminDisabled()
