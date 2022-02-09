from typing import List, Any

from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class S3PublicACLWrite(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure the S3 bucket does not allow WRITE permissions to everyone"
        id = "CKV_AWS_57"
        supported_resources = ("AWS::S3::Bucket",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_forbidden_values(self) -> List[Any]:
        return ["PublicReadWrite"]

    def get_inspected_key(self) -> str:
        return "Properties/AccessControl"


check = S3PublicACLWrite()
