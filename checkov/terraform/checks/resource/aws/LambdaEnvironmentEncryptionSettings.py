from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult,CheckCategories
from typing import List


class LambdaEnvironmentEncryptionSettings(BaseResourceCheck):

    def __init__(self):
        name = "Check encryption settings for Lambda environmental variable"
        id = "CKV_AWS_173"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # check that if I have env vars I have a KMS key
        if len(conf.get('environment', [])) > 0:
            if 'kms_key_arn' in conf:
                if len(conf["kms_key_arn"]) == 0:
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.FAILED

        #no env vars so should be no key as that causes state mismatch
        if 'kms_key_arn' in conf:
            if len(conf["kms_key_arn"]) == 0:
                return CheckResult.PASSED
            return CheckResult.FAILED
        # neither env vars nor kms key
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> List[str]:
        return ['environment/[0]/variables']


check = LambdaEnvironmentEncryptionSettings()
