from checkov.common.models.consts import ANY_VALUE

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AppConfigReplica(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure App configuration has at least one replica configured."
        id = "CKV_AZURE_242"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "replica/[0]/name"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AppConfigReplica()
