from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DataFactoryUsesGitRepository(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Data Factory uses Git repository for source control"
        id = "CKV_AZURE_103"
        supported_resources = ['azurerm_data_factory']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "github_configuration/[0]/repository_name"

    def get_expected_value(self):
        return ANY_VALUE


check = DataFactoryUsesGitRepository()
