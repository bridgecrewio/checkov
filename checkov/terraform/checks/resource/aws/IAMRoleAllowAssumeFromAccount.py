import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import extract_policy_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):

    def __init__(self):
        name = "Ensure IAM role allows only specific principals in account to assume it"
        id = "CKV_AWS_61"
        supported_resources = ['aws_iam_role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if not conf.get('assume_role_policy') or not isinstance(conf['assume_role_policy'][0], str):
            return CheckResult.PASSED
        try:
            assume_role_block = extract_policy_dict(conf['assume_role_policy'][0])
            if assume_role_block and 'Statement' in assume_role_block.keys() \
                    and 'Principal' in assume_role_block['Statement'][0] \
                    and 'AWS' in assume_role_block['Statement'][0]['Principal']:
                account_access = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')
                if re.match(account_access, assume_role_block['Statement'][0]['Principal']['AWS']):
                    return CheckResult.FAILED
        except Exception:  # nosec
            pass
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['assume_role_policy']


check = IAMRoleAllowAssumeFromAccount()
