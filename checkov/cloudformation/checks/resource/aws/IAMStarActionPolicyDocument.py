from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
import ast


class IAMStarActionPolicyDocument(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_63"
        supported_resources = ['AWS::IAM::Policy', 'AWS::IAM::Group', 'AWS::IAM::Role', 'AWS::IAM::User']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        myproperties = conf.get("Properties")
        type = conf['Type']

        # catch for inline policies
        if type != 'AWS::IAM::Policy':
            if isinstance(myproperties, dict) and 'Policies' in myproperties.keys():
                policies = myproperties['Policies']
                if len(policies) > 0:
                    for policy in policies:
                        if not isinstance(policy, dict):
                            return CheckResult.UNKNOWN
                        if policy.get('PolicyDocument'):
                            result = check_policy(policy['PolicyDocument'])
                            if result == CheckResult.FAILED:
                                return result
                    return CheckResult.PASSED
                # not empty and had non failing policies
                return CheckResult.UNKNOWN
        # this is just for Policy resources
        if isinstance(myproperties, dict) and 'PolicyDocument' in myproperties.keys():
            return check_policy(myproperties['PolicyDocument'])
        return CheckResult.UNKNOWN


check = IAMStarActionPolicyDocument()


def check_policy(policy_block):
    if policy_block:
        if isinstance(policy_block, str):
            policy_block = ast.literal_eval(policy_block)
        if 'Statement' in policy_block.keys():
            for statement in force_list(policy_block['Statement']):
                if 'Action' in statement and statement.get('Effect', ['Allow']) == 'Allow' and '*' in force_list(
                        statement['Action']):
                    return CheckResult.FAILED
                return CheckResult.PASSED
        else:
            return CheckResult.PASSED
    else:
        return CheckResult.PASSED
