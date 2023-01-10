from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureServicebusLocalAuthDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure Azure Service Bus Local Authentication is disabled"

        # This is the Unique ID for your check
        id = "CKV_AZURE_203"

        # These are the Terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ("azurerm_servicebus_namespace",)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "local_auth_enabled"

    def get_expected_value(self) -> Any:
        return False


check = AzureServicebusLocalAuthDisabled()
