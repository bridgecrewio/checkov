from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EventgridTopicLocalAuthentication(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Event Grid Topic local Authentication is disabled"
        id = "CKV_AZURE_192"
        supported_resources = ['azurerm_eventgrid_topic']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, )

    def get_inspected_key(self):
        return 'local_auth_enabled'

    def get_expected_value(self):
        return False


check = EventgridTopicLocalAuthentication()
