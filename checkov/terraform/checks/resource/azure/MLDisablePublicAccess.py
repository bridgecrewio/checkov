from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MLDisablePublicAccess(BaseResourceValueCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Ensure that Public Access is disabled for Machine Learning Workspace"

        # This is the Unique ID for your check
        id = "CKV_AZURE_144"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['azurerm_machine_learning_workspace']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self):
        return False

check = MLDisablePublicAccess()