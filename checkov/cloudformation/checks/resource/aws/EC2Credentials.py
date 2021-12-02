from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.secrets import string_has_secrets, AWS

class EC2Credentials(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no hard-coded secrets exist in EC2 user data"
        id = "CKV_AWS_46"
        supported_resources = ['AWS::EC2::Instance']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'UserData' in conf['Properties'].keys():
                user_data = conf['Properties']['UserData']
                # Cast to string as user data object can look slightly different depending
                # on Yaml or JSON CF Templates and how the B64 conversion is done.
                user_data_str = str(user_data)
                if isinstance(user_data_str, str):
                    if string_has_secrets(user_data_str):
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/UserData"]


check = EC2Credentials()
