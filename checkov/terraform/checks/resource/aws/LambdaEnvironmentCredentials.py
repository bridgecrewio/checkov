from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.secrets import string_has_secrets, AWS
from checkov.common.util.type_forcers import force_list


class LambdaEnvironmentCredentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard-coded secrets exists in lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = 'environment/[0]/variables'
        if 'environment' in conf.keys():
            if isinstance(conf['environment'][0], dict):
                if 'variables' in conf['environment'][0]:
                    if isinstance(force_list(conf['environment'][0]['variables'])[0], dict):
                        # variables can be a string, which in this case it points to a variable
                        for values in list(force_list(conf['environment'][0]['variables'])[0].values()):
                            for value in list(filter(lambda value: isinstance(value, str), force_list(values))):
                                if string_has_secrets(value, AWS):
                                    return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()
