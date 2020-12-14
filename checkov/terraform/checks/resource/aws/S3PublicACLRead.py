from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class S3PublicACLRead(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "S3 Bucket has an ACL defined which allows public READ access."
        id = "CKV_AWS_20"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'acl'

    def get_forbidden_values(self):
        return ["public-read", "public-read-write", "website", "authenticated-read"]


check = S3PublicACLRead()
