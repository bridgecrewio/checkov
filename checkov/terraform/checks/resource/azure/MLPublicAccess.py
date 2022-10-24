from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class MLPublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure that Public Access is disabled for Machine Learning Workspace"

        # This is the Unique ID for your check
        id = "CKV_AZURE_144"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ('azurerm_machine_learning_workspace',)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_forbidden_values(self) -> list[Any]:
        return [True]


check = MLPublicAccess()
