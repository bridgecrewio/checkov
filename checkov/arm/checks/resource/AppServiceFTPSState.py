from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from typing import List


class AppServiceFTPSState(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure FTP deployments are disabled"
        id = "CKV_AZURE_78"
        supported_resources = ('Microsoft.Web/sites',)
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "siteConfig/ftpsState"

    def get_expected_value(self) -> str:
        return "Disabled"

    def get_expected_values(self) -> List[str]:
        return ["Disabled", "FtpsOnly"]


check = AppServiceFTPSState()
