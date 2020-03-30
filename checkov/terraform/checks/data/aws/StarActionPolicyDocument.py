from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class StarActionPolicyDocument(BaseDataCheck):
    def __init__(self):
        name = "Ensure IAM policies that allow \"*\" as the statement's actions are not created"
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
            for statement in conf['statement']:
                if '*' in statement['actions'] and statement['effect'][0] == "Allow":
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = StarActionPolicyDocument()
