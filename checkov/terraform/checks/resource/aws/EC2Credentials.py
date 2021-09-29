from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.secrets import string_has_secrets
from typing import List


class EC2Credentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard-coded secrets exist in EC2 user data"
        id = "CKV_AWS_46"
        supported_resources = ['aws_instance']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'user_data' in conf.keys():
            user_data = conf['user_data'][0]
            if isinstance(user_data, str) and string_has_secrets(user_data):
                return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['user_data']


check = EC2Credentials()
