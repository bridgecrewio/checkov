from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EventgridTopicIdentityProviderEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Managed identity provider is enabled event grid topic"
        id = "CKV_AZURE_194"
        supported_resources = ['azurerm_eventgrid_topic']
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "identity/[0]/type"

    def get_expected_value(self):
        return ANY_VALUE


check = EventgridTopicIdentityProviderEnabled()
