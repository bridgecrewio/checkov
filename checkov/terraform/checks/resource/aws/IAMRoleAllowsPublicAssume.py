from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import json


class IAMRoleAllowsPublicAssume(BaseResourceCheck):

    def __init__(self):
        name = "Ensure IAM role allows only specific services or principals to assume it"
        id = "CKV_AWS_60"
        supported_resources = ['aws_iam_role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('assume_role_policy') and isinstance(conf['assume_role_policy'][0], str):
            try:
                assume_role_block = json.loads(conf['assume_role_policy'][0])
                if 'Statement' in assume_role_block.keys():
                    for statement in assume_role_block['Statement']:
                        if 'Effect' in statement and statement['Effect'] == 'Deny':
                            continue
                        if 'AWS' in statement['Principal']:
                            # Can be a string or an array of strings
                            aws = statement['Principal']['AWS']
                            if (type(aws) == str and aws == '*') or (type(aws) == list and '*' in aws):
                                return CheckResult.FAILED
            except: # nosec
                pass
        return CheckResult.PASSED


check = IAMRoleAllowsPublicAssume()
