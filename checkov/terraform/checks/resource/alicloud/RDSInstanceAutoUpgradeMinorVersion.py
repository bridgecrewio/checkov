from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import List, Any


class RDSInstanceAutoUpgradeMinorVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RDS instance is set to auto upgrade minor versions"
        id = "CKV_ALI_34"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'auto_upgrade_minor_version'

    def get_expected_value(self) -> Any:
        return "Auto"


check = RDSInstanceAutoUpgradeMinorVersion()
