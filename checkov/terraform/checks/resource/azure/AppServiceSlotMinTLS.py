from typing import Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceSlotMinTLS(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the App service slot is using the latest version of TLS encryption"
        id = "CKV_AZURE_154"
        supported_resources = ['azurerm_app_service_slot']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "site_config/[0]/min_tls_version/[0]"

    def get_expected_value(self):
        return '1.2'

    def get_expected_values(self) -> List[Any]:
        return ["1.2", 1.2, "1.3", 1.3]


check = AppServiceSlotMinTLS()
