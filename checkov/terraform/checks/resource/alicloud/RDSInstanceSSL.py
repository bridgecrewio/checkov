from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import List, Any


class RDSInstanceSSL(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RDS instance uses SSL"
        id = "CKV_ALI_20"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ssl_action'

    def get_expected_values(self) -> List[Any]:
        return ["Open", "Update"]


check = RDSInstanceSSL()
