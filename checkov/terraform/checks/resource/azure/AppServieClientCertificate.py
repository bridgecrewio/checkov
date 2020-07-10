from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceClientCertificate(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the web app has 'Client Certificates (Incoming client certificates)' set"
        id = "CKV_AZURE_17"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'client_cert_enabled/[0]'


check = AppServiceClientCertificate()
