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
                for value in conf['environment'][0]['variables'][0].values():
                    if re.match(access_key_pattern, value) or re.match(secret_key_pattern, value):
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()
