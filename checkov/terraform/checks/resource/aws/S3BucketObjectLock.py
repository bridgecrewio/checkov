from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class S3BucketObjectLock(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that S3 bucket has lock configuration enabled by default"
        id = "CKV_AWS_143"
        supported_resources = ["aws_s3_bucket"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        lock_conf = conf.get("object_lock_configuration")
        if lock_conf and lock_conf[0]:
            lock_enabled = lock_conf[0].get("object_lock_enabled")
            if lock_enabled in ["Enabled", ["Enabled"]]:
                return CheckResult.PASSED
            return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = S3BucketObjectLock()
