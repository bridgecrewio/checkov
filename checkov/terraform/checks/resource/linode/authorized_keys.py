from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AuthorizedKeys(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure SSH key set in authorized_keys"
        id = "CKV_LIN_2"
        supported_resources = ["linode_instance"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "authorized_keys"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AuthorizedKeys()
