from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import json


class IAMRoleAttachedToService(BaseResourceCheck):

    def __init__(self):
        name = "Ensure IAM Role is attached to a specific service"
        id = "CKV_AWS_60"
        supported_resources = ['aws_iam_role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if isinstance(conf['assume_role_policy'][0], str):
            try:
                assume_role_block = json.loads(conf['assume_role_policy'][0])
                if 'Statement' in assume_role_block.keys():
                    if 'Principal' in assume_role_block['Statement'][0]:
                        if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                            if assume_role_block['Statement'][0]['Principal']['AWS'] == '*':
                                    return CheckResult.FAILED
            except:
                pass
        return CheckResult.PASSED


check = IAMRoleAttachedToService()
