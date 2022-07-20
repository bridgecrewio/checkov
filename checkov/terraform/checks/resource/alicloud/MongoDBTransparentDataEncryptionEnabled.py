from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class MongoDBTransparentDataEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MongoDB has Transparent Data Encryption Enabled"
        id = "CKV_ALI_44"
        supported_resources = ['alicloud_mongodb_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "tde_status"

    def get_expected_value(self) -> Any:
        return "enabled"


check = MongoDBTransparentDataEncryptionEnabled()
