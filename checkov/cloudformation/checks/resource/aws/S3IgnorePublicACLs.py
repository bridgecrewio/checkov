from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3IgnorePublicACLs(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure S3 bucket has ignore public ACLs enabled"
        id = "CKV_AWS_55"
        supported_resources = ("AWS::S3::Bucket",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/PublicAccessBlockConfiguration/IgnorePublicAcls"


check = S3IgnorePublicACLs()
