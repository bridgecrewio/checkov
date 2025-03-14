from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list


class IAMAdminPolicyDocument(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no IAM policies that allow full \"*-*\" administrative privileges are not created"
        id = "CKV_AWS_62"
        supported_resources = ['AWS::IAM::Policy', 'AWS::IAM::Group', 'AWS::IAM::Role', 'AWS::IAM::User']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        my_properties = conf.get("Properties")
        type = conf['Type']

        # catch for inline policies
        if isinstance(my_properties, dict) and type != 'AWS::IAM::Policy':
            self.evaluated_keys = ['Properties']
            if 'Policies' in my_properties.keys():
                self.evaluated_keys = ['Properties/Policies']
                policies = my_properties['Policies']
                if len(policies) > 0:
                    for idx, policy in enumerate(policies):
                        if not isinstance(policy, dict):
                            return CheckResult.UNKNOWN
                        if policy.get('PolicyDocument'):
                            self.evaluated_keys = [f'Properties/Policies/[{idx}]/PolicyDocument']
                            result = check_policy(policy['PolicyDocument'])
                            if result == CheckResult.FAILED:
                                return result
                    return CheckResult.PASSED
                # not empty and had non failing policies
                return CheckResult.UNKNOWN
        # this is just for Policy resources
        if isinstance(my_properties, dict) and 'PolicyDocument' in my_properties.keys():
            self.evaluated_keys = ['Properties/PolicyDocument']
            return check_policy(my_properties['PolicyDocument'])
        return CheckResult.UNKNOWN


check = IAMAdminPolicyDocument()


def check_policy(policy_block):
    if policy_block and isinstance(policy_block, dict) and 'Statement' in policy_block.keys():
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
