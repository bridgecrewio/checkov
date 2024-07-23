from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CognitiveServicesDisablesPublicNetwork(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that all Azure Cognitive Services accounts are configured with a managed identity"
        id = "CKV_AZURE_238"
        supported_resources = ['azurerm_cognitive_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "identity/[0]/type"

    def get_expected_value(self):
        return ANY_VALUE


check = CognitiveServicesDisablesPublicNetwork()
