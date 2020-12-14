import re
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.serverless.checks.function.base_function_check import BaseFunctionCheck
from checkov.common.models.consts import access_key_pattern, secret_key_pattern
from checkov.serverless.parsers.parser import ENVIRONMENT_TOKEN


class AWSCredentials(BaseFunctionCheck):

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists in provider"
        id = "CKV_AWS_41"
        supported_entities = ['serverless_aws']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_function_conf(self, conf):
        """
        see: https://www.terraform.io/docs/providers/aws/index.html#static-credentials
        """
        if conf.get(ENVIRONMENT_TOKEN):
            env_variables_strings = {key: value for key, value in conf.get(ENVIRONMENT_TOKEN).items() if
                                     isinstance(value, str)}
            for env_var_value in env_variables_strings.values():
                if any([re.match(access_key_pattern, env_var_value), re.match(secret_key_pattern, env_var_value)]):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AWSCredentials()
