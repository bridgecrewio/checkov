from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3MFADelete(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure S3 bucket has MFA delete enabled"
        id = "CKV_AWS_52"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "versioning/[0]/mfa_delete"


scanner = S3MFADelete()
