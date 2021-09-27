from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list

class IAMAdminPolicyDocument(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_63"
        supported_resources = ['AWS::IAM::Policy','AWS::IAM::Group','AWS::IAM::Role','AWS::IAM::User']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        myproperties=conf['Properties']
        type = conf['Type']

        #catch for inline policies
        if type != 'AWS::IAM::Policy':
             if 'Policies' in myproperties.keys():
                policies=myproperties['Policies']
                if len(policies) > 0:
                    for policy in policies:

                        result=check_policy(policy['PolicyDocument'])
                        if result==CheckResult.FAILED:
                           return result
                    return CheckResult.PASSED
                  # not empty and had non failing policies
                return CheckResult.UNKNOWN
        #this is just for Policy resources
        if 'PolicyDocument' in myproperties.keys():
            return check_policy(myproperties['PolicyDocument'])
        return CheckResult.UNKNOWN


check = IAMAdminPolicyDocument()

def check_policy(policy_block):
        if policy_block and 'Statement' in policy_block.keys():
            for statement in force_list(policy_block['Statement']):
                if 'Action' in statement:
                    effect = statement.get('Effect', 'Allow')
                    action = force_list(statement.get('Action', ['']))
                    resource = force_list(statement.get('Resource', ['']))
                    if effect == 'Allow' and '*' in action and '*' in resource:
                        return CheckResult.FAILED
            return CheckResult.PASSED
        else:
            return CheckResult.PASSED