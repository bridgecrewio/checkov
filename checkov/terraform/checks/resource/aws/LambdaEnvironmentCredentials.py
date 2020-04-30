import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.utils.consts import access_key_pattern, secret_key_pattern


class LambdaEnvironmentCredentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists in lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'environment' in conf.keys():
            if 'variables' in conf['environment'][0]:
                if type (conf['environment'][0]['variables']) is not list:
                    conf['environment'][0]['variables'] = [conf['environment'][0]['variables']]
                if type(conf['environment'][0]['variables'][0]) is dict:
                    # variables can be a string, which in this case it points to a variable
                    for values in list(conf['environment'][0]['variables'][0].values()):
                        if type(values) is not list:
                            values = [values]
                        for value in values:
                            if re.match(access_key_pattern, value) or re.match(secret_key_pattern, value):
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()
