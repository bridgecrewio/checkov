from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class SpaceBucketPublicRead(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure the Spaces bucket is private"
        id = "CKV_DIO_3"
        supported_resources = ['digitalocean_spaces_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "acl"

    def get_forbidden_values(self) -> List[Any]:
        return ["public-read"]


check = SpaceBucketPublicRead()
