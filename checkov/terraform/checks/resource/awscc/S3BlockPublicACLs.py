from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class S3BlockPublicACLs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure S3 bucket has block public ACLS enabled"
        id = "CKV_AWS_53"
        supported_resources = ("awscc_s3_bucket",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "public_access_block_configuration/block_public_acls"

    def get_expected_value(self):
        return True


check = S3BlockPublicACLs()
