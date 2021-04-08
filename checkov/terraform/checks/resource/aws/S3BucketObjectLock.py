from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class S3BucketObjectLock(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that S3 bucket has lock configuration enabled by default"
        id = "CKV_AWS_143"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'object_lock_configuration' in conf:
            if 'object_lock_enabled' in conf['object_lock_configuration'][0]:
                lock = conf['object_lock_configuration'][0]['object_lock_enabled']
                if lock == "Enabled":
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = S3BucketObjectLock()
