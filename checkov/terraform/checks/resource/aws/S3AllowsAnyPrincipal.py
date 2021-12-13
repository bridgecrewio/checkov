from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json
from typing import List


class S3AllowsAnyPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure S3 bucket does not allow an action with any Principal"
        id = "CKV_AWS_70"
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
                    if statement['Effect'] == 'Deny' or 'Principal' not in statement:
                        continue

                    principal = statement['Principal']
                    if principal == '*':
                        return CheckResult.FAILED
                    if 'AWS' in statement['Principal']:
                        # Can be a string or an array of strings
                        aws = statement['Principal']['AWS']
                        if (isinstance(aws, str) and aws == '*') or (isinstance(aws, list) and '*' in aws):
                            return CheckResult.FAILED
        except Exception: # nosec
            pass
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['policy']


check = S3AllowsAnyPrincipal()
