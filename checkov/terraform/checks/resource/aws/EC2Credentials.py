import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.utils.consts import access_key_pattern, secret_key_pattern


class EC2Credentials(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no hard coded AWS access key and and secret key exists in EC2 user data"
        id = "CKV_AWS_46"
        supported_resources = ['aws_instance']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'user_data' in conf.keys():
            user_data = conf['user_data'][0]
            if isinstance(user_data, str):
                if re.match(".*{}.*".format(access_key_pattern), conf['user_data'][0], re.DOTALL) or re.match(
                        ".*{}.*".format(secret_key_pattern), conf['user_data'][0], re.DOTALL):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = EC2Credentials()
