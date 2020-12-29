import json
import re

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM role allows only specific principals in account to assume it"
        id = "CKV_AWS_61"
        supported_resources = ['AWS::IAM::Role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'AssumeRolePolicyDocument' in conf['Properties']:
            if isinstance(conf['Properties']['AssumeRolePolicyDocument'], dict) and 'Fn::Sub' in conf['Properties']['AssumeRolePolicyDocument'].keys():
                assume_role_block = json.loads(conf['Properties']['AssumeRolePolicyDocument']['Fn::Sub'])
                if 'Statement' in assume_role_block.keys():
                    if isinstance(assume_role_block['Statement'], list) and 'Principal' in \
                            assume_role_block['Statement'][0]:
                        if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                            account_access = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')
                            if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                                if isinstance(assume_role_block['Statement'][0]['Principal']['AWS'],
                                              list) and isinstance(
                                    assume_role_block['Statement'][0]['Principal']['AWS'][0], str):
                                    if re.match(account_access,
                                                assume_role_block['Statement'][0]['Principal']['AWS'][0]):
                                        return CheckResult.FAILED
            else:
                if isinstance(conf['Properties']['AssumeRolePolicyDocument'], str):
                    assume_role_block = json.loads(conf['Properties']['AssumeRolePolicyDocument'])
                else:
                    assume_role_block = conf['Properties']['AssumeRolePolicyDocument']
                if 'Statement' in assume_role_block.keys():
                    if isinstance(assume_role_block['Statement'], list) and 'Principal' in \
                            assume_role_block['Statement'][0]:
                        if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                            account_access = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')
                            if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                                if isinstance(assume_role_block['Statement'][0]['Principal']['AWS'],
                                              list) and isinstance(
                                    assume_role_block['Statement'][0]['Principal']['AWS'][0], str):
                                    if re.match(account_access,
                                                assume_role_block['Statement'][0]['Principal']['AWS'][0]):
                                        return CheckResult.FAILED

            return CheckResult.PASSED


check = IAMRoleAllowAssumeFromAccount()
