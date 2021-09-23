from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudStorageSelfLogging(BaseResourceCheck):
    def __init__(self):
        name = "Bucket should not log to itself"
        id = "CKV_GCP_63"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        bucket_name = conf['name']
        #check for logging
        if 'logging' in conf:
            self.evaluated_keys = ['logging']
            if conf['logging'][0]:
                log_bucket_name = conf['logging'][0]['log_bucket']
                self.evaluated_keys = ['logging/[0]/log_bucket', 'name']
                if log_bucket_name != bucket_name:
                    return CheckResult.PASSED
                return CheckResult.FAILED
            return CheckResult.FAILED
        return CheckResult.UNKNOWN

check = CloudStorageSelfLogging()
