from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list, extract_policy_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMStarActionPolicyDocument(BaseResourceCheck):

    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_63"
        supported_resources = ['aws_iam_role_policy', 'aws_iam_user_policy', 'aws_iam_group_policy', 'aws_iam_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' in conf.keys():
            try:
                policy_block = extract_policy_dict(conf['policy'][0])
                if policy_block and 'Statement' in policy_block.keys():
                    for statement in force_list(policy_block['Statement']):
                        if 'Action' in statement and \
                                statement.get('Effect', ['Allow']) == 'Allow' and \
                                '*' in force_list(statement['Action']):
                            return CheckResult.FAILED
            except:  # nosec
                pass
        return CheckResult.PASSED


check = IAMStarActionPolicyDocument()
