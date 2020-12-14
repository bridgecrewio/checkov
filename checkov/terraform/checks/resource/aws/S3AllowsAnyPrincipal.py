from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json


class S3AllowsAnyPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure S3 bucket does not allow an action with any Principal"
        id = "CKV_AWS_70"
        supported_resources = ['aws_s3_bucket', 'aws_s3_bucket_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' in conf.keys():
            if isinstance(conf['policy'][0], str):
                try:
                    policy_block = json.loads(conf['policy'][0])
                    if 'Statement' in policy_block.keys():
                        for statement in force_list(policy_block['Statement']):
                            if statement['Effect'] == 'Deny':
                                continue
                            if 'Principal' not in statement:
                                continue

                            principal = statement['Principal']

                            if principal == '*':
                                return CheckResult.FAILED
                            elif 'AWS' in statement['Principal']:
                                # Can be a string or an array of strings
                                aws = statement['Principal']['AWS']
                                if (type(aws) == str and aws == '*') or (type(aws) == list and '*' in aws):
                                    return CheckResult.FAILED
                except: # nosec
                    pass
        return CheckResult.PASSED


check = S3AllowsAnyPrincipal()
