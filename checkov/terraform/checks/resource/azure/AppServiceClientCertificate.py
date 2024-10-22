from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceClientCertificate(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the web app has 'Client Certificates (Incoming client certificates)' set"
        id = "CKV_AZURE_17"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        if self.entity_type == 'azurerm_app_service':
            return 'client_cert_enabled/[0]'
        else:
            return 'client_certificate_enabled/[0]'


check = AppServiceClientCertificate()
