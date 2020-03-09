from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3Versioning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket have versioning enabled"
        id = "CKV_AWS_21"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "versioning/[0]/enabled"


scanner = S3Versioning()
