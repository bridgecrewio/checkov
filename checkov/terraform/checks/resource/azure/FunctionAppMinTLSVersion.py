from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Function app is using the latest version of TLS encryption"
        id = "CKV_AZURE_145"
        supported_resources = ['azurerm_function_app']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "site_config/[0]/min_tls_version"

    def get_expected_value(self):
        return 1.2

    def get_expected_values(self):
        return ["1.2", 1.2]


check = FunctionAppMinTLSVersion()
