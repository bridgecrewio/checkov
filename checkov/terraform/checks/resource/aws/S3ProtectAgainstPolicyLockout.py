from __future__ import annotations

import json
from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class S3ProtectAgainstPolicyLockout(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure S3 bucket policy does not lockout all but root user. (Prevent lockouts needing root account fixes)"
        id = "CKV_AWS_93"
        supported_resources = ('aws_s3_bucket', 'aws_s3_bucket_policy')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if 'policy' not in conf.keys() or not isinstance(conf['policy'][0], str):
            return CheckResult.PASSED
        try:
            policy_block = json.loads(conf['policy'][0])
            if 'Statement' in policy_block.keys():
                for statement in force_list(policy_block['Statement']):
                    if 'Condition' in statement.keys() or 'NotAction' in statement.keys() \
                            or statement.get('Effect') != 'Deny':
                        # https://github.com/bridgecrewio/checkov/pull/627#issuecomment-714681751
                        continue

                    principal = statement['Principal']
                    if principal == '*':
                        return CheckResult.FAILED
                    if 'AWS' in statement['Principal']:
                        # Can be a string or an array of strings
                        aws = statement['Principal']['AWS']
                        if (isinstance(aws, str) and aws == '*') or (isinstance(aws, list) and '*' in aws):
                            return CheckResult.FAILED

                    action = statement['Action']
                    if action == '*':
                        return CheckResult.FAILED
                    if 's3' in statement['Action']:
                        # Can be a string or an array of strings
                        s3 = statement['Action']['s3']
                        if (isinstance(s3, str) and s3 == '*') or (isinstance(s3, list) and '*' in s3):
                            return CheckResult.FAILED
        except Exception:  # nosec
            pass
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ['policy']


check = S3ProtectAgainstPolicyLockout()
