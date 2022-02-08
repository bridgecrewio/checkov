from typing import List, Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.consts import ANY_VALUE


class SecretsEncrypted(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        #  -from github docs "It is also advised that you do not store plaintext values in your code but rather populate
        #  the encrypted_value using fields from a resource, data source or variable as,
        #  while encrypted in state, these will be easily accessible in your code"
        name = "Ensure Secrets are encrypted"
        id = "CKV_GIT_4"
        supported_resources = ["github_actions_environment_secret",
                               "github_actions_organization_secret",
                               "github_actions_secret"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "plaintext_value"

    def get_forbidden_values(self) -> List[Any]:
        return [ANY_VALUE]


check = SecretsEncrypted()
