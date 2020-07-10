from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3BlockPublicACLs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure S3 bucket has block public ACLS enabled"
        id = "CKV_AWS_53"
        supported_resources = ['aws_s3_bucket_public_access_block']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "block_public_acls"


scanner = S3BlockPublicACLs()
