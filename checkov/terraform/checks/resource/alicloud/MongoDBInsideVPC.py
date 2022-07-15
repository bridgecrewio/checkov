from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class MongoDBInsideVPC(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MongoDB is deployed inside a VPC"
        id = "CKV_ALI_41"
        supported_resources = ['alicloud_mongodb_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "network_type"

    def get_expected_value(self) -> Any:
        return "VPC"


check = MongoDBInsideVPC()
