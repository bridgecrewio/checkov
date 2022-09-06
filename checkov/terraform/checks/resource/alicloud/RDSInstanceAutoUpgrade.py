from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class RDSInstanceAutoUpgrade(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS instance auto upgrades for minor versions"
        id = "CKV_ALI_30"
        supported_resources = ("alicloud_db_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "auto_upgrade_minor_version"

    def get_expected_value(self) -> Any:
        return "Auto"


check = RDSInstanceAutoUpgrade()
