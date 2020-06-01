from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

# rotation_period time unit is seconds
ONE_DAY = 24 * 60 * 60
NINETY_DAYS = 90 * ONE_DAY


class GoogleKMSKeyRotationPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Ensure KMS encryption keys are rotated within a period of 90 days"
        id = "CKV_GCP_43"
        supported_resources = ['google_kms_crypto_key']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'rotation_period' in conf.keys():
            time = int(conf['rotation_period'][0][:-1])
            if ONE_DAY <= time <= NINETY_DAYS:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleKMSKeyRotationPeriod()
