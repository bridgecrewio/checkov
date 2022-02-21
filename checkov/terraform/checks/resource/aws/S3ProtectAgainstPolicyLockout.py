from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json
from typing import List


class S3ProtectAgainstPolicyLockout(BaseResourceCheck):

    def __init__(self):
        name = "Ensure S3 bucket policy does not lockout all but root user. (Prevent lockouts needing root account fixes)"
        id = "CKV_AWS_93"
        supported_resources = ['aws_s3_bucket', 'aws_s3_bucket_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
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
                        if (type(aws) == str and aws == '*') or (type(aws) == list and '*' in aws):
                            return CheckResult.FAILED

                    action = statement['Action']
                    if action == '*':
                        return CheckResult.FAILED
                    if 's3' in statement['Action']:
                        # Can be a string or an array of strings
                        s3 = statement['Action']['s3']
                        if (type(s3) == str and s3 == '*') or (type(s3) == list and '*' in s3):
                            return CheckResult.FAILED
        except Exception:  # nosec
            pass
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['policy']


check = S3ProtectAgainstPolicyLockout()
