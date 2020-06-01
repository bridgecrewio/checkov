from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

NINETY_DAYS = {'d': 90, 'h': 2160, 'm': 129600, 's': 7776000}
ONE_DAY = {'d': 1, 'h': 24, 'm': 1440, 's': 86400}

class GoogleKMSKeyRotationPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Ensure KMS encryption keys are rotated within a period of 90 days"
        id = "CKV_GCP_44"
        supported_resources = ['google_kms_crypto_key']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'rotation_period' in conf.keys():
            time_unit = conf['rotation_period'][0][-1]
            time = int(conf['rotation_period'][0][:-1])
            if ONE_DAY[time_unit] <= time <= NINETY_DAYS[time_unit]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleKMSKeyRotationPeriod()
