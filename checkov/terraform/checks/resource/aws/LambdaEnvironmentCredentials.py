from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.secrets import string_has_secrets, AWS, GENERAL
from checkov.common.util.type_forcers import force_list
from typing import List


class LambdaEnvironmentCredentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard-coded secrets exist in lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if len(conf.get('environment', [])) > 0 and isinstance(conf['environment'][0], dict) \
                and 'variables' in conf['environment'][0] \
                and isinstance(force_list(conf['environment'][0]['variables'])[0], dict):
            # variables can be a string, which in this case it points to a variable
            for values in list(force_list(conf['environment'][0]['variables'])[0].values()):
                for value in list(filter(lambda value: isinstance(value, str), force_list(values))):
                    if string_has_secrets(value, AWS, GENERAL):
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['environment/[0]/variables']


check = LambdaEnvironmentCredentials()
