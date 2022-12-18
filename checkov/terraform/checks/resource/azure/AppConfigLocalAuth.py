from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class AppConfigLocalAuth(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        """
        Every request to an Azure App Configuration resource must be authenticated.
        By default, requests can be authenticated with either Azure Active Directory (Azure AD) credentials,
        or by using an access key. Of these two types of authentication schemes,
        Azure AD provides superior security and ease of use over access keys, and is recommended by Microsoft.
        """
        name = "Ensure 'local_auth_enabled' is set to 'False'"
        id = "CKV_AZURE_184"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "local_auth_enabled"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = AppConfigLocalAuth()
