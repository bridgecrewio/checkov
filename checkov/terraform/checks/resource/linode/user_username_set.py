from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class UsernameExists(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure username is set"
        id = "CKV_LIN_4"
        supported_resources = ["linode_user"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "username"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = UsernameExists()
