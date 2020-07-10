from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceHttps20Enabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'HTTP Version' is the latest if used to run the web app"
        id = "CKV_AZURE_18"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'site_config/[0]/http2_enabled'


check = AppServiceHttps20Enabled()
