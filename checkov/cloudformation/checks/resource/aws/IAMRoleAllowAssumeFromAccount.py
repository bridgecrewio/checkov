from __future__ import annotations

import json
import re
from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

ACCOUNT_ACCESS = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')


class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS IAM policy does not allow assume role permission across all services"
        id = "CKV_AWS_61"
        supported_resources = ('AWS::IAM::Role',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ['Properties']
        properties = conf.get('Properties')
        if properties and 'AssumeRolePolicyDocument' in properties:
            assume_role_policy_doc = properties['AssumeRolePolicyDocument']
            if isinstance(assume_role_policy_doc, dict) and 'Fn::Sub' in assume_role_policy_doc.keys():
                policy_fn_sub_block = assume_role_policy_doc['Fn::Sub']
                if isinstance(policy_fn_sub_block, list) and len(policy_fn_sub_block) == 2:
                    assume_role_block = json.loads(policy_fn_sub_block[0])
                else:
                    assume_role_block = json.loads(policy_fn_sub_block)
            elif isinstance(assume_role_policy_doc, str):
                try:
                    assume_role_block = json.loads(assume_role_policy_doc)
                except Exception:
                    return CheckResult.UNKNOWN
            else:
                assume_role_block = assume_role_policy_doc
        else:
            return CheckResult.UNKNOWN

        if 'Statement' in assume_role_block.keys():
            if isinstance(assume_role_block['Statement'], list) and 'Principal' in \
                    assume_role_block['Statement'][0]:
                if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                    if isinstance(assume_role_block['Statement'][0]['Principal']['AWS'], list) \
                            and isinstance(assume_role_block['Statement'][0]['Principal']['AWS'][0], str):
                        if re.match(ACCOUNT_ACCESS, assume_role_block['Statement'][0]['Principal']['AWS'][0]):
                            self.evaluated_keys = ['Properties/AssumeRolePolicyDocument/Statement']
                            return CheckResult.FAILED

            return CheckResult.PASSED


check = IAMRoleAllowAssumeFromAccount()
