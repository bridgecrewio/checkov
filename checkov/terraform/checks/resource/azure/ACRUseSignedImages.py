from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ACRUseSignedImages(BaseResourceValueCheck):

    def __init__(self):
        # IN ARM - Set properties.policies.trustPolicy.status to enabled, set
        # properties.policies.trustPolicy.type to Notary
        # This is the default behaviour by the tf provider when the trust policy is enabled
        name = "Ensures that ACR uses signed/trusted images"
        id = "CKV_AZURE_164"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "trust_policy_enabled"

    def get_expected_value(self) -> Any:
        return True


check = ACRUseSignedImages()
