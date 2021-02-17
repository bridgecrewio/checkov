from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudStorageLogging(BaseResourceCheck):
    def __init__(self):
        name = "Bucket should log access"
        id = "CKV_GCP_62"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        #check fot logging
        if 'logging' in conf.keys():
            if conf['logging'][0]['log_bucket']:
                log_bucket_name = conf['logging'][0]['log_bucket']
                if log_bucket_name != None:
                    return CheckResult.PASSED
                else:
                   return CheckResult.FAILED
            else:
                return CheckResult.FAILED
            return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.FAILED

check = CloudStorageLogging()
