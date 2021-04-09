from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

class S3BucketObjectLock(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that S3 bucket has lock configuration enabled by default"
        id = "CKV_AWS_143"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'object_lock_configuration/[0]/object_lock_enabled/[0]'

    def get_expected_value(self):
        return 'Enabled'

check = S3BucketObjectLock()
