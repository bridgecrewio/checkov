from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json


class IAMAdminPolicyDocument(BaseResourceCheck):

    def __init__(self):
        name = "Ensure IAM policies that allow full \"*-*\" administrative privileges are not created"
        id = "CKV_AWS_62"
        supported_resources = ['aws_iam_role_policy', 'aws_iam_user_policy', 'aws_iam_group_policy', 'aws_iam_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' in conf.keys():
            try:
                policy_block = json.loads(conf['policy'][0])
                if 'Statement' in policy_block.keys():
                    for statement in force_list(policy_block['Statement']):
                        if 'Action' in statement:
                            effect = statement.get('Effect', 'Allow')
                            action = force_list(statement.get('Action', ['']))
                            resource = force_list(statement.get('Resource', ['']))
                            if effect == 'Allow' and '*' in action and '*' in resource:
                                return CheckResult.FAILED
            except:  # nosec
                pass
        return CheckResult.PASSED


check = IAMAdminPolicyDocument()
