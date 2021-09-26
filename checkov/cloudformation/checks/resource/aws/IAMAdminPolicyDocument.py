import json

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list, extract_policy_dict

class IAMAdminPolicyDocument(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_63"
        supported_resources = ['AWS::IAM::Policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        myproperties=conf['Properties']
        if 'PolicyDocument' in myproperties.keys():
            policy_block = myproperties['PolicyDocument']
            try:
                if policy_block and 'Statement' in policy_block.keys():
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
