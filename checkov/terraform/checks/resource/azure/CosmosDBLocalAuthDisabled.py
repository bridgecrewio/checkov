from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CosmosDBLocalAuthDisabled(BaseResourceValueCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Ensure that Local Authentication is disabled on CosmosDB"

        # This is the Unique ID for your check
        id = "CKV_AZURE_140"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['azurerm_cosmosdb_account']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.IAM]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "local_authentication_disabled"
        
    def get_expected_value(self):
        return True

check = CosmosDBLocalAuthDisabled()