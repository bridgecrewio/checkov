import re
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.checks.base_function_check import BaseFunctionCheck
from checkov.common.models.consts import access_key_pattern, secret_key_pattern


class AWSCredentials(BaseFunctionCheck):

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists in provider"
        id = "CKV_AWS_41"
        supported_entities = ['serverless_aws']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories,  supported_entities=supported_entities)

    def scan_function_conf(self, conf):
        """
        see: https://www.terraform.io/docs/providers/aws/index.html#static-credentials
        """
        # TODO
        # if self.secret_found(conf, "access_key", access_key_pattern):
        #     return CheckResult.FAILED
        # if self.secret_found(conf, "secret_key", secret_key_pattern):
        #     return CheckResult.FAILED
        # return CheckResult.PASSED

    @staticmethod
    def secret_found(conf, field, pattern):
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                return True
        return False


check = AWSCredentials()
