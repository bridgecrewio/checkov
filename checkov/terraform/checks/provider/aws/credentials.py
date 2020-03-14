import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class AWSCredentials(BaseProviderCheck):
    access_key_pattern = "(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])"
    secret_key_pattern = "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists"
        id = "CKV_AWS_41"
        supported_provider = ['aws']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf):
        """
        see: https://www.terraform.io/docs/providers/aws/index.html#static-credentials
        """
        if self.secret_found(conf, "access_key", self.access_key_pattern):
            return CheckResult.FAILED
        if self.secret_found(conf, "secret_key", self.secret_key_pattern):
            return CheckResult.FAILED
        return CheckResult.PASSED

    @staticmethod
    def secret_found(conf, field, pattern):
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                return True
        return False


check = AWSCredentials()
