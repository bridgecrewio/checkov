from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MSSQLServerMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MSSQL is using the latest version of TLS encryption"
        id = "CKV_AZURE_52"
        supported_resources = ['azurerm_mssql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "minimum_tls_version"

    def get_expected_value(self):
        return "1.2"


check = MSSQLServerMinTLSVersion()
