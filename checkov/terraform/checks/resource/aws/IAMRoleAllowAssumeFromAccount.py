from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import json
import re


class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):

    def __init__(self):
        name = "Ensure IAM role allows only specific principals in account to assume it"
        id = "CKV_AWS_61"
        supported_resources = ['aws_iam_role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('assume_role_policy') and isinstance(conf['assume_role_policy'][0], str):
            try:
                assume_role_block = json.loads(conf['assume_role_policy'][0])
                if 'Statement' in assume_role_block.keys():
                    if 'Principal' in assume_role_block['Statement'][0]:
                        if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                            account_access = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')
                            if re.match(account_access, assume_role_block['Statement'][0]['Principal']['AWS']):
                                return CheckResult.FAILED
            except: # nosec
                pass
        return CheckResult.PASSED


check = IAMRoleAllowAssumeFromAccount()
