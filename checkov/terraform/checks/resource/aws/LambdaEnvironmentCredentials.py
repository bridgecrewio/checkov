import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.utils.consts import access_key_pattern, secret_key_pattern
from checkov.common.util.type_forcers import force_list


class LambdaEnvironmentCredentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists in lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'environment' in conf.keys():
            if isinstance(conf['environment'][0], dict):
                if 'variables' in conf['environment'][0]:
                    if isinstance(force_list(conf['environment'][0]['variables'])[0], dict):
                        # variables can be a string, which in this case it points to a variable
                        for values in list(force_list(conf['environment'][0]['variables'])[0].values()):
                            for value in list(filter(lambda value: isinstance(value, str), force_list(values))):
                                if re.match(access_key_pattern, value) or re.match(secret_key_pattern, value):
                                    return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()
