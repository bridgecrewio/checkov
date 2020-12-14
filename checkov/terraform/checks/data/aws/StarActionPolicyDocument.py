from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class StarActionPolicyDocument(BaseDataCheck):
    def __init__(self):
        name = "Ensure no IAM policies documents allow \"*\" as a statement's actions"
        id = "CKV_AWS_49"
        supported_data = ['aws_iam_policy_document']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf):
        """
            validates iam policy document
            https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        key = 'statement'
        if key in conf.keys():
            for statement in conf[key]:
                if 'actions' in statement and '*' in statement['actions'][0] and statement.get('effect', ['Allow'])[0] == 'Allow':
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = StarActionPolicyDocument()
